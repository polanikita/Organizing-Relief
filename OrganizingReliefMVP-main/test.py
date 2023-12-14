
currUser = "Francis"
error_message = 'ERROR'
with open('pages/citizenHome.html', 'r') as file:
    html_content = file.read().replace('{{ error_message }}', error_message)
    html_content2 = html_content.replace('{{ civilian_name }}', currUser)
print(html_content2)