from schema import schema
import json

introspection_dict = schema.introspect()

fp = open("schema.json", "w")
fp.write(json.dump(introspection_dict))
fp.close()
