# test.py

query1 = "SELECT * FROM users WHERE id = 1"
query2 = "SELECT * FROM users WHERE id = 1; DROP TABLE users"
query3 = f"SELECT * FROM users WHERE id = {user_input}"
query4 = "SELECT * FROM users WHERE id = %s" % user_input

def execute_query(query):
    # Code here
    pass

execute_query(query1)
execute_query(query2)
execute_query(query3)
execute_query(query4.join(user_input_list))
