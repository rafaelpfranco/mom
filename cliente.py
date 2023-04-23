from flask import Flask, render_template, request, redirect
from flask_cors import CORS
import pika
import os
import threading, json

def start_rabbit():
    os.system("rabbitmqctl.bat stop_app")
    os.system("rabbitmqctl.bat reset")
    os.system("rabbitmqctl.bat start_app")

app = Flask(__name__)
start_rabbit()
CORS(app, resources={r"/*": {"origins": "*", "methods": "*"}})

connection = pika.BlockingConnection(
    pika.ConnectionParameters(host='localhost'))
channel = connection.channel()

clients = []
exceptionTopic = ['amq.topic', 'amq.rabbitmq.trace']
exceptionQueue = ['joÃ£o', 'style.css']
msgs = {}
topics = {}

@app.route("/", methods=["POST", "GET"])
def main():
    if request.method == "POST":
        name = request.form["name"]
        if name in clients:
            return redirect('client/'+ name)
    return render_template('login.html')

@app.route("/client/<string:name>")
def chat(name):
    t = threading.Thread(target=start_consuming_thread, args=(name,))
    t.start()
    return render_template('client.html', queues = listQueues(), clientName = name, topics = listTopics(), msgs = msgs, topicSub = topics) 

@app.route("/client/<string:name>/send/<string:dest>", methods=["POST"])
def send(name, dest):
    message = request.form["inputMsg"]
    channel.basic_publish(exchange='', routing_key=dest, body= name + ':'+ message + '\n')
    if dest in msgs[name].keys():
        msgs[name][dest] += name + ':'+ message + '\n'
    else:
        msgs[name][dest] = name + ':'+ message + '\n'

    return redirect('/client/'+ name)
  
@app.route("/admin", methods=["POST", "GET"])
def admin():  
    if request.method == "POST":    
        newClientName = request.form["newClientName"]
        if newClientName != None:  
            if newClientName not in clients:
                clients.append(newClientName)
                msgs[newClientName] = {}
                topics[newClientName] = []
                channel.queue_declare(newClientName)
    return render_template('admin.html', clients = clients, queues = listQueues(), topics = listTopics())  

@app.route("/admin/deleteclient", methods=["POST"])
def deleteClient():
    if request.method == "POST":    
        clientName = str(request.form["clientName"])
        if clientName:
            clients.remove(clientName)
            channel.queue_delete(clientName)
            return redirect('/admin')
        else:
            return redirect('/admin')

@app.route("/admin/deletequeue", methods=["POST"])
def deleteQueue():
    if request.method == "POST":    
        queueName = str(request.form["queueName"])
        if queueName:
            channel.queue_delete(queueName)
            return redirect('/admin')
        else:
            return redirect('/admin')  

@app.route("/admin/newqueue", methods=["POST"])
def newQueue():
    if request.method == "POST":    
        newQueueName = str(request.form["clientNameForQueue"])
        if newQueueName:
            channel.queue_declare(newQueueName)
            return redirect('/admin')
        else:
            return redirect('/admin')  

@app.route("/admin/newtopic", methods=["POST"])
def newTopic():
    if request.method == "POST":    
        newTopic = str(request.form["newTopic"])
        if newTopic:
            channel.exchange_declare(exchange=newTopic, exchange_type='topic')
            msgs[newTopic] = {}
            return redirect('/admin')
        else:
            return redirect('/admin')  

@app.route("/admin/deletetopic", methods=["POST"])
def deleteTopic():
    if request.method == "POST":    
        topicName = str(request.form["topicName"])
        if topicName:
            channel.exchange_delete(topicName)
            return redirect('/admin')
        else:
            return redirect('/admin') 

@app.route("/client/<string:name>/subtopic", methods=["POST"])
def subTopic(name):
    selected_topic = request.form['topicSelect']
    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = connection.channel()
    channel.queue_bind(exchange=selected_topic, queue=name, routing_key=selected_topic)
    if selected_topic not in topics[name]:
        topics[name].append(selected_topic)
        print(topics)
    return redirect('/client/'+ name)
    

@app.route("/api/login", methods=["POST"])
def login():
    name = request.get_json().name
    if name in clients:
        return "", 200
    return "", 400

def listQueues():
    stream = os.popen("rabbitmqctl.bat list_queues")
    output = stream.read()
    queuesRaw = output.split("name\tmessages")[1].split("\n")
    queues = []
    for linha in queuesRaw:
        if len(linha.split("\t")) > 1:
            if linha.split("\t")[0] not in exceptionQueue:
                queues.append({"name": linha.split("\t")[0], "msgs": linha.split("\t")[1]})
    return queues

def listTopics():
    stream = os.popen("rabbitmqctl.bat list_exchanges")
    output = stream.read()
    topicsRaw = output.split("name\ttype")[1].split("\n")
    topics = []
    for linha in topicsRaw:
        if len(linha.split("\t")) > 1:
            if linha.split("\t")[1] == "topic" and linha.split("\t")[0] not in exceptionTopic:
                topics.append({"name": linha.split("\t")[0]})
    return topics


def start_consuming_thread(name):
    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    
    def callback(ch, method, properties, body):
        # Processar a mensagem aqui
        m = body.decode("utf-8")
        remet = m.split(":", 1)[0]
        if remet in msgs[name].keys():
            msgs[name][remet] += body.decode("utf-8")
        else:
            msgs[name][remet] = body.decode("utf-8")

    channel = connection.channel()
    channel.queue_declare(queue=name)
    channel.basic_consume(queue=name, on_message_callback=callback, auto_ack=True)
    channel.start_consuming()

if __name__ == "__main__":
    app.run(debug=True)

