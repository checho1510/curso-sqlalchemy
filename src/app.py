from flask import Flask, request, jsonify
from flask.typing import TemplateFilterCallable
from flask_sqlalchemy import SQLAlchemy # ORM
from flask_marshmallow import Marshmallow # Define un esquema con el cual vamos a interactuar

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root@localhost/flaskmysql' # Cadena de conexión
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False # Evita warnings cuando ejecutemos el programa

db = SQLAlchemy(app) # Inicializamos el ORM y nos devuelve una instancia de la base de datos que guardamos en db
ma = Marshmallow(app) # Instanciamos esquema

# Definimos qué es lo que vamos a guardar en la base de datos
class Task(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    title = db.Column(db.String(70), unique = True)
    description = db.Column(db.String(100))

    def __init__(self, title, description):
        self.title = title
        self.description = description

db.create_all() # este método lee todas las clases y a partir de ellas crea las tablas

# Creamos un esquema para interactuar facilmente con la db
class TaskSchema(ma.Schema):
    class Meta:
        fields = ('id', 'title', 'description')

task_schema = TaskSchema() # cuando quiera trabajar con una tarea voy a interactuar con este objeto
tasks_schema = TaskSchema(many = True) # objeto para interactuar con muchas tareas

###################### ROUTES ##########################

@app.route('/tasks', methods=['POST'])
def create_task():

    # Recibo desde el request las variables para crear una nueva task
    title = request.json['title']
    description = request.json['description']
    
    # Creo una task con los valores
    new_task = Task(title, description)

    # Guardo la task en la base de datos
    db.session.add(new_task)
    db.session.commit()

    return task_schema.jsonify(new_task) # Respondemos la tarea al cliente para que vea lo que hemos creado

@app.route('/tasks', methods=['GET'])
def get_tasks():
    all_tasks = Task.query.all()
    result = tasks_schema.dump(all_tasks)
    return jsonify(result)

@app.route('/tasks/<id>', methods=['GET'])
def get_task(id):
    task = Task.query.get(id)
    return task_schema.jsonify(task)

@app.route('/tasks/<id>', methods=['PUT'])
def update_task(id):
    task = Task.query.get(id)

    title = request.json['title']
    description = request.json['description']

    task.title = title
    task.description = description

    db.session.commit()

    return task_schema.jsonify(task)

@app.route('/tasks/<id>', methods=['DELETE'])
def delete_task(id):
    task = Task.query.get(id)
    db.session.delete(task)
    db.session.commit()

    return task_schema.jsonify(task)

@app.route('/', methods=['GET'])
def index():
    return jsonify({'message': 'Welcome to my REST API'})

if __name__ == '__main__':
    app.run(debug=True)