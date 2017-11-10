#!/usr/bin/python

import MySQLdb
import sys

def get_col_charset(words):
    for i in xrange(0, len(words)):
        if words[i] == 'CHARACTER' and words[i + 1] == 'SET':
            return words[i + 2]
    return ''

def rechartable(cursor, tablename, charset):
    cursor.execute("show create table " + tablename)
    tabledesc = cursor.fetchall()[0][1]
    cols = tabledesc[tabledesc.find('(') + 1:tabledesc.rfind(')')]
    tablecharset = tabledesc[tabledesc.rfind(')') + 1:]
    tablecharset = tablecharset[tablecharset.find('DEFAULT CHARSET=') + 16:]

    spaceIndex = tablecharset.find(' ')
    if spaceIndex != -1:
        tablecharset = tablecharset[:spaceIndex]

    if tablecharset != charset:
        command = "ALTER TABLE `" + tablename + "` DEFAULT CHARACTER SET " + charset
        print "EXEC SQL CMD:", command
        cursor.execute(command)
        return rechartable(cursor, tablename, charset)

    print "Now, Table " + tablename + " Charset is " + tablecharset
    cols = cols.split('\n')
    for col in cols:
        col = col.strip()
        if len(col) == 0:
            continue
        if col[0] != '`':
            continue

        chindex = col.find('CHARACTER SET')
        if chindex == -1:
            continue

        words = col.split(' ')
        colname = words[0]
        curset = get_col_charset(words)

        if curset != charset:
            print "Column " + colname + " Charset is " + curset
            newcol = col.replace('CHARACTER SET ' + curset, 'CHARACTER SET ' + charset)
            if newcol[-1] == ',':
                newcol = newcol[0:-1]

            command = "ALTER TABLE `" + tablename + "` CHANGE " + colname + " " + newcol
            print "EXEC SQL CMD:", command
            cursor.execute(command)

def rechardatabase(host, user, pwd, db, charset):
    db = MySQLdb.connect(host = host, user = user, passwd = pwd, db = db)
    cursor = db.cursor()
    cursor.execute("show tables")

    tables = cursor.fetchall()
    for row in tables:
        tablename = row[0]
        rechartable(cursor, tablename)

    db.close()

if __name__ == "__main__":
    if len(sys.argv) < 6:
        print sys.argv[0], " mysqlhost mysqluser mysqlpass mysqldatabase targetcharset"
        sys.exit(0)

    rechardatabase(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5])


