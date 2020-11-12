#!/usr/bin/env python3

import datetime
from html.parser import HTMLParser
from io import StringIO
import json
import logging
import os
import re
import sys

# To remove markup
# https://stackoverflow.com/questions/753052/strip-html-from-strings-in-python
class MLStripper(HTMLParser):
    def __init__(self):
        super().__init__()
        self.reset()
        self.strict = False
        self.convert_charrefs= True
        self.text = StringIO()
    def handle_data(self, d):
        self.text.write(d)
    def get_data(self):
        return self.text.getvalue()

class Entry:
    def __init__(self, **kwargs):
        self.root = False
        self.id = None
        self.type = None
        self.creation_time = None
        self.title = ""
        self.content = ""
        self.references = []
        self.contributors = []
        self.endorsements = []
        self.nonstudent_endorsements = []
        self.children = []
        self.changes_count = 0
        self.tags = []
        self.views = 0
        self.parent = None

        for key in kwargs:
            setattr(self, key, kwargs[key])

    def get_id(self):
        id = str(self.id)

        if self.parent:
            id += "." + self.parent.get_id()

        return id

    def remove_markup(self, content):
        s = MLStripper()
        s.feed(content)
        return s.get_data()

    def normalize(self, content):
        remove_unwanted_chars = re.sub('[^\w\s]', "", self.remove_markup(content)).lower()
        word_list = list(filter(None, remove_unwanted_chars.split(' ')))

        return word_list

    def get_full_normalized_text(self):
        all_content = self.normalize(self.title + " " + self.content + " ")

        for child in self.children:
            all_content += child.get_full_normalized_text()

        return all_content

    def get_contributors(self, target=None):
        contributors = []
        if not target:
            target = self

        contributors += target.contributors

        for child in self.children:
            contributors += child.contributors

        return contributors

    def get_endorsers(self, target=None):
        endorsers = []
        if not target:
            target = self

        endorsers += target.endorsements

        for child in self.children:
            endorsers += child.endorsements

        return endorsers

    def get_references(self, target=None):
        references = []
        if not target:
            target = self

        references += target.references

        for child in self.children:
            references += child.references

        return references


    def get_top_level(self):
        toReturn = ""

        toReturn += "{} {} -- Tags: {} -- Created: {} - # of modifications: {}, views: {} \n".format(self.type, self.get_id(), self.tags, self.creation_time, self.changes_count, self.views)
        toReturn += self.get_entry_details()

        toReturn += self.get_children()

        return toReturn

    def get_entry_details(self):
        toReturn = ""

        toReturn += "{} -- {}\n".format(self.remove_markup(self.title), self.remove_markup(self.content))
        toReturn += "Normalized text: {}\n".format(self.get_full_normalized_text())
        toReturn += "References: {}\n".format(self.get_references())
        toReturn += "Contributors: {}\n".format(self.get_contributors())
        toReturn += "Endorsements: {}\n".format(self.get_endorsers())

        return toReturn


    def get_answer_by_type(self, type=None):
        toReturn = ""
        ALL_OTHER_TYPES = [Post.FOLLOWUP_ANSWER_ID, Post.FEEDBACK_ANSWER_ID]

        if type:
            for child in self.children:
                if child.id == type:
                    toReturn += child.get_entry_details()
        else:
            for cur in ALL_OTHER_TYPES:
                toReturn += self.get_answer_by_type(cur)

        return toReturn


    def get_children(self):
        toReturn = ""

        instructor = self.get_answer_by_type(Post.FRIENDLY_INSTRUCTOR_ANSWER_ID)
        if instructor:
            toReturn += "\n>>\nInstructor Answer: {}\n<<\n".format(instructor)

        student = self.get_answer_by_type(Post.FRIENDLY_STUDENT_ANSWER_ID)
        if student:
            toReturn += "\n>>\nStudent Answer: {}\n<<\n".format(student)

        all_others = self.get_answer_by_type()
        if all_others:
            toReturn += "\n>>\nOther: {}\n<<\n".format(all_others)


        return toReturn


    def __str__(self):
        return self.get_top_level()


class Post:
    ID_KEY = 'nr'
    TYPE_KEY = 'type'
    CREATION_KEY = 'created'
    NO_SUBJECT_TYPES = []
    HISTORY_KEY = 'history'
    SUBJECT_KEY = 'subject'
    CONTENT_KEY = 'content'
    TOPLEVEL_USER_ID = 'id'
    CHILD_USER_ID = 'uid'
    ANONYMOUS_USER_ID_KEY = 'uid_a'
    VIEWS_KEY = 'unique_views'
    CHANGES_KEY = 'change_log'
    ENDORSEMENT_ARRAY_KEY = 'tag_endorse_arr'
    GOOD_ARRAY_KEY = 'tag_good_arr'
    TAGS_KEY = 'tags'
    CHILDREN_KEY = 'children'
    STUDENT_ANSWER_ID = 's_answer'
    FRIENDLY_STUDENT_ANSWER_ID = 'student_answer'
    INSTRUCTOR_ANSWER_ID = 'i_answer'
    FRIENDLY_INSTRUCTOR_ANSWER_ID = 'instructor_answer'
    FOLLOWUP_ANSWER_ID = 'followup'
    FEEDBACK_ANSWER_ID = 'feedback'
    DUPLICATE_ANSWER_ID = 'dupe'

    storage = None
    post = None
    entry = None

    def __init__(self, postDict, path):
        self.post = postDict
        self.storage = path

    def construct_entry(self, target=None, id=None):
        is_root = False
        if not target:
            target=self.post
            is_root=True

        if not id:
            id = self.id(target)

        entry = Entry(
            # sourcedata=self.post,
            root=is_root,
            id=id,
            type=self.type(target),
            creation_time=self.creation(target),
            title=self.subject(target),
            content=self.content(target),
            references=self.find_references(target),
            contributors=self.users(target),
            changes_count=self.changes(target),
            endorsements=self.endorsements(target),
        )

        # Gather items only on root
        if target == self.post:
            entry.views = self.views()
            entry.tags = self.tags()

        if not self.entry:
            self.entry = entry

        for child in target[self.CHILDREN_KEY]:
            childEntry = self.construct_entry(child, self.id(child))
            childEntry.parent = entry
            entry.children.append(childEntry)

        return entry

    def id(self, target):
        if target == self.post:
            return self.post[self.ID_KEY]
        else:
            # TODO: Cleanup
            type = self.type(target)
            if type == self.STUDENT_ANSWER_ID:
                return self.FRIENDLY_STUDENT_ANSWER_ID
            elif type == self.INSTRUCTOR_ANSWER_ID:
                return self.FRIENDLY_INSTRUCTOR_ANSWER_ID
            elif type == self.FOLLOWUP_ANSWER_ID:
                return self.FOLLOWUP_ANSWER_ID
            elif type == self.FEEDBACK_ANSWER_ID:
                return self.FEEDBACK_ANSWER_ID
            elif type == self.DUPLICATE_ANSWER_ID:
                return self.DUPLICATE_ANSWER_ID

        return "Error"

    def type(self, target=None):
        if not target:
            target = self.post

        return target[self.TYPE_KEY]

    def creation(self, target):
        if not target:
            target = self.post
        return target[self.CREATION_KEY]

    def subject(self, target=None):
        FIRST_HISTORY = 0
        root = False

        if target == self.post:
            root = True

        if not target:
            target = self.post

        toReturn = ""
        if self.type(target) in self.NO_SUBJECT_TYPES:
            return None
        else:
            # TODO: What to do if there are multiple history entries?
            toReturn = target.get(self.HISTORY_KEY, [{self.SUBJECT_KEY:''}])[FIRST_HISTORY][self.SUBJECT_KEY]

        return toReturn

    def content(self, target=None):
        FIRST_HISTORY = 0
        TYPES_USING_SUBJECT = [self.FEEDBACK_ANSWER_ID, self.FOLLOWUP_ANSWER_ID, self.DUPLICATE_ANSWER_ID]

        if not target:
            target = self.post

        if self.type(target) in TYPES_USING_SUBJECT:
            return target[self.SUBJECT_KEY]
        else:
            # TODO: What to do if there are multiple history entries?
            return target[self.HISTORY_KEY][FIRST_HISTORY][self.CONTENT_KEY]

    def users(self, target=None):
        FIRST_HISTORY = 0
        TYPES_WITH_NO_HISTORY = [self.FOLLOWUP_ANSWER_ID, self.FEEDBACK_ANSWER_ID, self.DUPLICATE_ANSWER_ID]
        if not target:
            target = self.post

        users = []

        if target == self.post:
            users.append(target[self.TOPLEVEL_USER_ID])
        else:
            # TODO: What to do if there are multiple history entries?
            if self.type(target) in TYPES_WITH_NO_HISTORY:
                try:
                    users.append(target[self.CHILD_USER_ID])
                except:
                    users.append(target[self.ANONYMOUS_USER_ID_KEY])
            else:
                try:
                    users.append(target[self.HISTORY_KEY][FIRST_HISTORY][self.CHILD_USER_ID])
                except:
                    users.append(target[self.HISTORY_KEY][FIRST_HISTORY][self.ANONYMOUS_USER_ID_KEY])

        return users

    def find_references(self, target=None):
        if not target:
            target = self.post

        content = self.content(target)
        postRefs = re.findall('@(\d+)', content)
        externalRefs = re.findall('"(/redirect/[^"]*)', content)

        return postRefs + externalRefs

    def endorsements(self, target=None):
        if not target:
            target = self.post

        tag_endorsements = target.get(self.ENDORSEMENT_ARRAY_KEY, [])
        tag_good = target.get(self.GOOD_ARRAY_KEY, [])

        return tag_endorsements + tag_good

    def views(self):
        return self.post[self.VIEWS_KEY]

    def changes(self, target=None):
        if not target:
            target=self.post
        return len(target.get(self.CHANGES_KEY, []))

    def tags(self):
        return self.post[self.TAGS_KEY]

    def construct_child(self, child):
        pass

    def __str__(self):
        return self.storage + "\n" + str(self.entry)

def openpost(path):
    with open(path, 'r') as f:
        post = Post(json.load(f), path)
        post.construct_entry()
        return post


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)

    default_dir = datetime.datetime.now().strftime("%Y_%m_%d")

    single_post = os.environ.get('SINGLE_POST', False)
    base_dir = os.environ.get('BASE_DIR', '.')
    target_date = os.environ.get('TARGET_DATE', default_dir)
    course_network = sys.argv[1]

    effective_dir = "{}/{}/{}".format(base_dir, course_network, target_date)
    logging.info("Processing directory: " + effective_dir)

    with open(effective_dir + "/summary.txt", 'w') as out:
        logging.info("Creating: " + effective_dir + "/summary.txt")
        for entry in os.scandir(effective_dir):
            if (entry.path.endswith(".json")):
                post = openpost(entry.path)
                print(post)
                out.write(str(post))

                if single_post:
                    exit(0)


