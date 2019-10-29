
import json


with open('vita_input.json', 'r') as fh:
    vita_input = json.load(fh)


print()
print(vita_input['run_id'])
print(vita_input['run_date'])
print(vita_input['user'])
print()
print('Plasma Settings:')
print('- NBI Power -> {}'.format(vita_input['plasma-settings']['heating']['NBI-power']))
print('- Ohmic-power -> {}'.format(vita_input['plasma-settings']['heating']['Ohmic-power']))
print('- rf-power -> {}'.format(vita_input['plasma-settings']['heating']['rf-power']))
