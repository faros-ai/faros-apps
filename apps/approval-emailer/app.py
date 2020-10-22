from faros.client import FarosClient
from jinja2 import Environment, FileSystemLoader
import os
import json


def lambda_handler(event, context):
    client = FarosClient.from_event(event)
    params = event['params']
    recipient = params['recipient']
    text = params['text']
    link = 'https://pontus-git-cwu-demo.faros-ai.vercel.app/approval'

    file_loader = FileSystemLoader(os.path.dirname(__file__))
    env = Environment(loader=file_loader)
    template = env.get_template('email.html')
    html = template.render(text=text, link=link)

    subject = 'Faros AI notification'

    query = '''mutation($to: [String!]!, $subject: String!, $htmlBody: String!) {
        faros_send_email(
            to: $to
            subject: $subject
            textBody: "This report can only be seen in HTML enabled email clients"
            htmlBody: $htmlBody
        )
    }'''
    variables = {
        "to": [recipient],
        "subject": subject,
        "htmlBody": html
    }

    response = client.graphql_execute(query, variables)
    return response
