import yaml
import pymysql
import base64

db = yaml.safe_load(open('db.yaml'))
dbcon = pymysql.connect(host=db['mysql_host'], user=db['mysql_user'],
                        password=db['mysql_password'], db=db['mysql_db'])

cur=dbcon.cursor()

name='Avneesh Deshmukh'
intro='''Allow me to introduce Avneesh, a bright and ambitious IT student pursuing his education at the Modern College of Engineering. With an innate passion for technology and a relentless drive for continuous learning, Avneesh is on a mission to explore the vast possibilities that the field of Information Technology holds. From software development to data analysis, Avneesh embraces the ever-evolving landscape of IT with enthusiasm and determination. With a creative mindset and a knack for problem-solving, Avneesh is eager to make his mark, leveraging technology to drive positive change and shape the digital future.'''

insta='https://instagram.com/avneeshdeshmukh?igshid=ZDc4ODBmNjlmNQ=='

twitter='https://twitter.com/kungfukenny1745?t=0mfXY2wRu1bBu98wcZSgtQ&s=08'

linkedin='https://www.linkedin.com/in/avneesh-deshmukh-232a41236'

email='avneesh1745@gmail.com'

cur.execute(f"INSERT INTO dev(name, intro, insta, twitter, linkedin, email) VALUES('{name}', '{intro}', '{insta}', '{twitter}', '{linkedin}', '{email}' )")






dbcon.commit()
cur.close()