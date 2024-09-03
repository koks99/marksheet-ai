import re

from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def get_data_from_extracted_text(text):
    # Assuming each line of the table starts with a digit
    lines = re.findall(r'^\d+.*', text, re.MULTILINE)
    table = [line.split() for line in lines]
    texts = text.split(' ')
    name = ''
    roll_no = ''
    courses = []
    for i in range(len(texts)):
        if "name" in texts[i].lower():
            name = texts[i + 1]
        if texts[i].lower() == "roll":
            roll_no = texts[i + 2].splitlines()[0]
    for x in table:
        if len(x) > 4:
            course = ' '.join(x[:len(x) - 3])
            grade = x[len(x) - 2]
            course = course.replace('|', '')
            course = course.replace('!', 'I')
            grade = grade.replace('t', '+')
            grade = grade.replace('°', 'O')
            courses.append({"course": course, "grade": grade})
    return {"name": name, "roll_no": roll_no, "courses": courses}

def get_search_results(myquery, students_col):
    my_doc = students_col.find(myquery)
    results = []
    for x in my_doc:
        x.pop('_id', None)
        x.pop('visibility', None)
        results.append(x)
    return results