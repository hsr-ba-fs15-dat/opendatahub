import hub.nodes


h = hub.nodes.HttpInput('http://localhost:5000/sample/sample.csv')
c = hub.nodes.CsvInput()
d = hub.nodes.DatabaseWriter('Random garbage')

http_input = h.read()
csv_input = c.parse(http_input)
d.write(csv_input)
