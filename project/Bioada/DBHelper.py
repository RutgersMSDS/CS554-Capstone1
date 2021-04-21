import pymssql


class Singleton:
    def __init__(self, cls):
        self._cls = cls

    def Instance(self):
        try:
            return self._instance
        except AttributeError:
            self._instance = self._cls()
            return self._instance

    def __call__(self):
        raise TypeError('Singletons must be accessed through `Instance()`.')

    def __instancecheck__(self, inst):
        return isinstance(inst, self._cls)


@Singleton
class DBConnection():
    def __init__(self):
        server_url = '13.92.0.168'
        user_name = 'saedsayad'
        pwd = 'mordab1339235$'
        db_name = 'GSE13355'

        conn = pymssql.connect(server=server_url, user=user_name, password=pwd, database=db_name)
        self.cursor = conn.cursor()


"""
USAGE:
    c1 = DBConnection.Instance().cursor
    probeSQL = "SELECT PID FROM GSE13355.dbo.GSE13355_probes"
    c1.execute(probeSQL)

    probes = c1.fetchall()
"""