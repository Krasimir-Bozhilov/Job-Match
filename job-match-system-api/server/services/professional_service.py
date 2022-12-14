from server.data.database import read_query, update_query
from server.data.models import Professional, Role

from mariadb import DataError

def all(search: str | None = None, search_by: str | None = None):
    if search is None:
        data = read_query(
            '''SELECT u.id, u.user_name,u.email,u.phone,u.address,t.name,
            p.first_name,p.last_name,p.summary,p.busy
                FROM users as u
                LEFT JOIN professionals as p 
                ON u.id= p.user_id
                LEFT JOIN towns as t
                ON t.id=u.town_id
                WHERE u.role=?''',(Role.PROFESSIONAL,))
    else:
        if search_by != 'town_name':
                data = read_query(
                f'''SELECT u.id, u.user_name,u.email,u.phone,u.address,t.name,
                p.first_name,p.last_name,p.summary,p.busy
                FROM users as u
                LEFT JOIN professionals as p 
                ON u.id= p.user_id
                LEFT JOIN towns as t    
                ON t.id=u.town_id
               WHERE u.role=? AND p.{search_by} LIKE ?''', (Role.PROFESSIONAL,f'%{search}%'))
    
        else:
                data = read_query(
                f'''SELECT u.id, u.user_name,u.email,u.phone,u.address,t.name,
                p.first_name,p.last_name,p.summary,p.busy
                FROM users as u
                LEFT JOIN professionals as p 
                ON u.id= p.user_id
                LEFT JOIN towns as t    
                ON t.id=u.town_id
               WHERE u.role=? AND t.name LIKE ?''', (Role.PROFESSIONAL,f'%{search}%'))

    if not data:
        return None

    return (Professional.from_query_result(*row) for row in data)


def get_professional_by_id(id: int,read_data=None):
    if read_data is None:
        read_data = read_query

    read_data(
        '''SELECT u.id, u.user_name,u.email,u.phone,u.address,t.name,
            p.first_name,p.last_name,p.summary,p.busy
                FROM users as u
                LEFT JOIN professionals as p 
                ON u.id= p.user_id
                LEFT JOIN towns as t
                ON t.id=u.town_id
            WHERE u.id=? and u.role =?''', (id,Role.PROFESSIONAL))

    return next((Professional.from_query_result(*row) for row in read_data), None)


def edit_professional(id:int,professional: Professional,update_data=None):
    if update_data is None:
        update_data = update_query
    try:
        update_data(
        '''UPDATE professionals
            SET first_name = ?,last_name=?,summary=?,busy=?
             WHERE user_id = ?''', (professional.first_name, professional.last_name,
                                    professional.summary,professional.busy,
                                    id))

        return True
    
    except DataError:
        return False

def make_professional_busy(professional_id:int, update_data=update_query):
    return update_data('''UPDATE professionals
            SET busy= ?
            WHERE user_id = ?''', (1, professional_id))



def sort(professionals: list[Professional], *, attribute='name', reverse=False):

    if attribute == 'name':
        def sort_fn(p: Professional): return p.first_name
    else:
        def sort_fn(p: Professional): return p.id

    return sorted(professionals, key=sort_fn, reverse=reverse)