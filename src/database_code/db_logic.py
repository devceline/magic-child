import sqlite3
import botconfig as b
import discord
import random
random.seed()


class db_commands:

    conn = sqlite3.connect(b.database_location)
    c = conn.cursor()
    xp_gain = [5, 10, 15, 20]

    def add_warning(self, member: discord.Member):
        try:
            self.c.execute("INSERT INTO {tn} ({idf}, {idm}, {cn}) "
                           "VALUES ({member_id}, '{member_name}', 1)"
                           .format(
                               tn=b.table_name,
                               idf=b.columns[1],
                               idm=b.columns[3],
                               member_name=member.name,
                               cn=b.columns[3],
                               member_id=member.id
                           )
                           )
        except sqlite3.IntegrityError:
            self.c.execute("UPDATE {tn} SET {cn} = {cn} + 1 "
                           "WHERE {idf}= {member_id}"
                           .format(
                               tn=b.table_name,
                               idf=b.columns[1],
                               cn=b.columns[3],
                               member_id=member.id
                           )
                           )
        finally:
            self.conn.commit()

    def read_warnings(self, message):
        self.c.execute('SELECT ({coi}) FROM {tn} WHERE {cn}={member_id}'
                       .format(
                           coi=b.columns[3],
                           tn=b.table_name,
                           cn=b.columns[1],
                           member_id=message.author.id
                       )
                       )
        member_warnings = self.c.fetchall()
        return member_warnings[0][0]

    def add_xp(self, message):
        members_name = str(message.author.name)
        try:
            self.c.execute("INSERT INTO {tn} ({idf}, {idm}, {cn}) "
                           "VALUES ({member_id}, '{member_name}', {xp})"
                           .format(
                               tn=b.table_name,
                               idf=b.columns[1],
                               idm=b.columns[2],
                               cn=b.columns[4],
                               member_id=message.author.id,
                               member_name=members_name,
                               xp=self.xp_gain[random.randrange(0, 4, 1)]
                           )
                           )
        except sqlite3.IntegrityError:
            self.c.execute("UPDATE {tn} SET {cn} = {cn} + {xp} "
                           "WHERE {idf}= {member_id}"
                           .format(
                               tn=b.table_name,
                               idf=b.columns[1],
                               cn=b.columns[4],
                               member_id=message.author.id,
                               xp=self.xp_gain[random.randrange(0, 4, 1)]
                           )
                           )
        finally:
            self.conn.commit()

    def read_xp(self, member: discord.Member):
        ''' This grabs xp of user and their level, applies level formula to xp to get lvl_end, and sends them as a tuple '''
        self.c.execute('SELECT ({coi}) FROM {tn} WHERE {cn}={member_id}'  # This grabs xp
                       .format(
                           coi=b.columns[4],
                           tn=b.table_name,
                           cn=b.columns[1],
                           member_id=member.id
                       )
                       )
        try:
            experience = self.c.fetchall()[0][0]
        except IndexError:
            self.chat_unmute(member)

        self.c.execute('SELECT ({coi}) FROM {tn} WHERE {cn}={member_id}'  # This grabs level.
                       .format(
                           coi=b.columns[5],
                           tn=b.table_name,
                           cn=b.columns[1],
                           member_id=member.id
                       )
                       )
        lvl_start = self.c.fetchall()[0][0]
        lvl_end = b.level_formula(experience)

        return (lvl_start, lvl_end)

    def level_up(self, member):
        ''' Adds one to level field '''
        self.c.execute("UPDATE {tn} SET {cn} = {cn} + 1 "
                       "WHERE {idf} = {member_id}"
                       .format(
                           tn=b.table_name,
                           idf=b.columns[1],
                           cn=b.columns[5],
                           member_id=member.id
                       )
                       )
        self.conn.commit()

    def chat_mute(self, member: discord.Member, minutes):
        self.c.execute("UPDATE {tn} SET {cn} = {mins} WHERE {idf} = {member_id}"
                       .format(
                           tn=b.table_name,
                           cn=b.columns[6],
                           mins=minutes,
                           idf=b.columns[1],
                           member_id=member.id
                       )
                       )

        self.conn.commit()

    def decrease_mute(self, member):
        self.c.execute("UPDATE {tn} SET {cn} = {cn} - 5 WHERE {idf} = {member_id}"
                       .format(
                           tn=b.table_name,
                           cn=b.columns[6],
                           idf=b.columns[1],
                           member_id=member.id
                       )
                       )
        self.conn.commit()

    def chat_unmute(self, member: discord.Member):
        ''' Sets Muted to 0 '''
        try:
            self.c.execute("INSERT INTO {tn} ({idf}, {idm}, {cn}) "
                           "VALUES ({member_id}, '{member_name}', 0)"
                           .format(
                               tn=b.table_name,
                               idf=b.columns[1],
                               idm=b.columns[2],
                               cn=b.columns[6],
                               member_id=member.id,
                               member_name=member.name
                           )
                           )

        except sqlite3.IntegrityError:
            self.c.execute("UPDATE {tn} SET {cn} = 0 WHERE {idf} = {member_id}"
                           .format(
                               tn=b.table_name,
                               idf=b.columns[1],
                               cn=b.columns[6],
                               member_id=member.id
                           )
                           )
        finally:
            self.conn.commit()

    def read_chat_mute(self, member):
        try:
            self.c.execute("SELECT {coi} FROM {tn} WHERE {cn}={member_id}"
                           .format(
                               coi=b.columns[6],
                               tn=b.table_name,
                               cn=b.columns[1],
                               member_id=member.id
                           )
                           )
            member_mute = self.c.fetchall()
            return member_mute[0][0]
        except IndexError:
            self.chat_unmute(member)
            return False

    def add_currency(self, member, amount):
        if int(amount) < 0:
            operation = "-"
            amount = str(int(amount) * -1)
        else:
            operation = "+"
        self.c.execute("UPDATE {tn} SET {cn} = {cn} {op} {_amount} WHERE {idf} = {member_id}"
                       .format(
                           tn=b.table_name,
                           cn=b.columns[7],
                           op=operation,
                           _amount=amount,
                           idf=b.columns[1],
                           member_id=member.id
                       )
                       )
        self.conn.commit()

    def deduct_currency(self, member, amount):
        self.c.execute("UPDATE {tn} SET {cn} = {cn} - {_amount} "
                       "WHERE {idf}= '{member_id}'"
                       .format(
                           tn=b.table_name,
                           idf=b.columns[1],
                           cn=b.columns[7],
                           _amount=amount,
                           member_id=member.id
                       )
                       )
        self.conn.commit()

    def get_balance(self, member):
        self.c.execute("SELECT ({coi}) FROM {tn} WHERE {idf}={member_id}"
                       .format(
                           coi=b.columns[7],
                           tn=b.table_name,
                           idf=b.columns[1],
                           member_id=member.id
                       )
                       )
        member_balance = self.c.fetchone()
        return member_balance[0]

    def leaderboards(self):
        self.c.execute("SELECT {member_name}, {amount} FROM {tn} ORDER BY {cn} DESC LIMIT 10"
                       .format(
                           member_name=b.columns[2],
                           amount=b.columns[7],
                           tn=b.table_name,
                           cn=b.columns[7]
                       )
                       )
        leaders = list(self.c.fetchall())
        return leaders

    def close_connection(self):
        self.conn.close()
