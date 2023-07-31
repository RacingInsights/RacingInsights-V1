from previous_versions.very_old_code import iracing

[ir_conn, state] = iracing.init_ir_connection()
# print(ir_conn['SessionInfo']['Sessions'][0]['ResultsPositions'][0]['LapsComplete'])
# while True:
nr_of_results = len(ir_conn['SessionInfo']['Sessions'][0]['ResultsPositions'])
# print(ir_conn['SessionInfo']['Sessions'][-1]['ResultsPositions'])
tires_fitted = [(int(tire) != -1) for tire in ir_conn['CarIdxTireCompound']]

print(tires_fitted)
# for i in range(0, nr_of_results):
#     car_id = ir_conn['SessionInfo']['Sessions'][0]['ResultsPositions'][i]['CarIdx']
#     driver_name = ir_conn['DriverInfo']['Drivers'][car_id]['UserName']
#     lap_time = ir_conn['SessionInfo']['Sessions'][0]['ResultsPositions'][i]['FastestTime']
#     print(driver_name,f"{lap_time}")

# Others:
# nr_of_results = len(ir['SessionInfo']['Sessions'][0]['ResultsPositions'])
# for i in range(0, nr_of_results):
# car_id = ir_conn['SessionInfo']['Sessions'][0]['ResultsPositions'][i]['CarIdx']
# driver_name = ir['DriverInfo']['Drivers'][car_id]['UserName']
# fastest_lap_time = ir['SessionInfo']['Sessions'][0]['ResultsPositions'][i]['FastestTime']
