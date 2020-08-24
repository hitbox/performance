import csv
import subprocess
import sys

class mdbreader:
    """
    Somewhat cross-platform Microsoft Access reader.
    """

    def __init__(self, mdb):
        self.mdb = mdb

    if sys.platform == 'win32':
        def read_table(self, table):
            import win32com.client
            dao = win32com.client.Dispatch('DAO.DBEngine.36')
            Options = 0
            ReadOnly = True
            db = dao.OpenDatabase(str(self.mdb), Options, ReadOnly)
            recordset = db.OpenRecordset(table)
            rows = []
            while not recordset.EOF:
                rows.append({field.Name: '' if field.Value is None else str(field.Value)
                             for field in recordset.Fields})
                recordset.MoveNext()
            return rows
    else:
        def read_table(self, table):
            # working around the fact that there are \r\n in the memo fields but
            # the \r is lost somewhere in the call.
            lineterm = '\n' * 128
            cmd = ['mdb-export',
                   '-D', '%Y-%m-%d %H:%M:%S',
                   '-R', lineterm,
                   self.mdb, table]
            output = subprocess.check_output(cmd, text=True)
            output = output.split(lineterm)
            return csv.DictReader(output)
