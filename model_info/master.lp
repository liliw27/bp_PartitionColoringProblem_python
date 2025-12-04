\ Model master
\ LP format - for model browsing. Use MPS format to capture full model detail.
Minimize
  T + 1000 column_1 + 1000 column_2 + 1000 column_3 + 1000 column_4
Subject To
 each_partition_colored_once_constraint0: column_1 + column_54 + column_55
   + column_94 + column_95 + column_104 + column_105 + column_1424
   + column_1425 + column_1455 + column_1456 + column_1483 + column_1484
   + column_1487 + column_1614 + column_1615 + column_1674 + column_1675
   + column_4504 + column_4505 + column_4510 + column_10349 + column_10387
   + column_10388 + column_10414 >= 1
 each_partition_colored_once_constraint1: column_2 + column_1487
   + column_1491 + column_4510 + column_10415 >= 1
 each_partition_colored_once_constraint2: column_3 + column_1422
   + column_1424 + column_1425 + column_4525 + column_4527 + column_10386
   + column_10387 + column_10390 >= 1
 each_partition_colored_once_constraint3: column_4 + column_4502
   + column_4503 + column_4504 + column_4505 + column_4510 + column_4524
   + column_4525 + column_4527 + column_10292 + column_10389 + column_10390
   + column_10391 + column_10416 + column_10417 >= 1
 each_partition_colored_once_constraint4: column_1 + column_143
   + column_10292 + column_10352 + column_10353 >= 1
 each_partition_colored_once_constraint5: column_2 + column_10342
   + column_10349 + column_10385 + column_10386 + column_10387
   + column_10388 + column_10389 + column_10390 + column_10391
   + column_10418 >= 1
 each_partition_colored_once_constraint6: column_3 + column_4524
   + column_4525 + column_10385 + column_10388 + column_10389
   + column_10391 >= 1
 each_partition_colored_once_constraint7: column_4 + column_10342
   + column_10349 + column_10352 + column_10353 >= 1
 each_partition_colored_once_constraint8: column_1 + column_1482
   + column_1483 + column_1484 + column_1487 + column_1491 + column_4524
   + column_4525 + column_4527 + column_10385 + column_10386 + column_10387
   + column_10388 + column_10389 + column_10390 + column_10391
   + column_10412 + column_10413 + column_10414 + column_10415
   + column_10416 + column_10417 + column_10418 >= 1
 each_partition_colored_once_constraint9: column_2 + column_53 + column_54
   + column_55 + column_4524 + column_4525 + column_4527 >= 1
 each_partition_colored_once_constraint10: column_3 + column_93 + column_94
   + column_95 + column_4524 + column_4525 + column_4527 + column_10292
   + column_10342 + column_10349 + column_10353 + column_10385
   + column_10386 + column_10387 + column_10388 + column_10389
   + column_10390 + column_10391 >= 1
 each_partition_colored_once_constraint11: column_4 + column_1433
   + column_10352 + column_10353 + column_10385 + column_10386
   + column_10387 + column_10388 + column_10389 + column_10390
   + column_10391 + column_10412 + column_10413 + column_10414
   + column_10415 + column_10416 + column_10417 + column_10418 >= 1
 each_partition_colored_once_constraint12: column_1 + column_10342
   + column_10349 + column_10352 + column_10353 >= 1
 each_partition_colored_once_constraint13: column_2 + column_4524
   + column_4525 + column_4527 >= 1
 each_partition_colored_once_constraint14: column_3 + column_1663
   + column_4524 + column_4527 + column_10385 + column_10386 + column_10387
   + column_10388 + column_10389 + column_10390 + column_10391
   + column_10412 + column_10413 + column_10414 + column_10415
   + column_10416 + column_10417 + column_10418 >= 1
 each_partition_colored_once_constraint15: column_4 + column_103
   + column_104 + column_105 + column_4524 + column_4525 + column_4527
   + column_10385 + column_10386 + column_10387 + column_10388
   + column_10389 + column_10390 + column_10391 + column_10412
   + column_10413 + column_10414 + column_10415 + column_10416
   + column_10417 + column_10418 >= 1
 each_partition_colored_once_constraint16: column_1 + column_10292
   + column_10342 + column_10349 + column_10352 + column_10353
   + column_10385 + column_10386 + column_10387 + column_10388
   + column_10389 + column_10390 + column_10391 + column_10412
   + column_10413 + column_10414 + column_10415 + column_10416
   + column_10417 + column_10418 >= 1
 each_partition_colored_once_constraint17: column_2 + column_1612
   + column_1614 + column_1615 + column_4524 + column_4525 + column_4527
   + column_10292 + column_10352 + column_10353 + column_10412
   + column_10413 + column_10414 + column_10415 + column_10416
   + column_10417 + column_10418 >= 1
 each_partition_colored_once_constraint18: column_3 + column_1673
   + column_1674 + column_1675 + column_4502 + column_4503 + column_4504
   + column_4505 + column_4510 + column_10342 + column_10349 + column_10352
   + column_10385 + column_10386 + column_10387 + column_10388
   + column_10389 + column_10390 + column_10391 >= 1
 each_partition_colored_once_constraint19: column_4 + column_1452
   + column_1454 + column_1455 + column_1456 + column_10292 + column_10385
   + column_10386 + column_10387 + column_10388 + column_10389
   + column_10390 + column_10391 + column_10412 + column_10413
   + column_10414 + column_10415 + column_10416 + column_10417
   + column_10418 >= 1
 makespan_vertex_0: T - column_1 - column_54 - column_94 - column_104
   - column_1424 - column_1455 - column_1483 - column_1487 - column_1614
   - column_1674 - column_4504 - column_4510 >= 0
 makespan_vertex_1: T - 5 column_55 - 5 column_95 - 5 column_105
   - 5 column_1425 - 5 column_1456 - 5 column_1484 - 5 column_1615
   - 5 column_1675 - 5 column_4505 - 5 column_10349 - 5 column_10387
   - 5 column_10388 - 5 column_10414 >= 0
 makespan_vertex_2: T - 2 column_2 >= 0
 makespan_vertex_3: T >= 0
 makespan_vertex_4: T >= 0
 makespan_vertex_5: T - 6 column_1487 - 6 column_1491 - 6 column_4510
   - 6 column_10415 >= 0
 makespan_vertex_6: T - 3 column_3 - 3 column_1422 - 3 column_1424
   - 3 column_1425 - 3 column_4525 - 3 column_4527 - 3 column_10386
   - 3 column_10387 - 3 column_10390 >= 0
 makespan_vertex_7: T >= 0
 makespan_vertex_8: T >= 0
 makespan_vertex_9: T >= 0
 makespan_vertex_10: T - 4 column_4 - 4 column_4502 - 4 column_4504
   - 4 column_4505 - 4 column_4510 - 4 column_4524 - 4 column_4525
   - 4 column_4527 - 4 column_10292 - 4 column_10389 - 4 column_10390
   - 4 column_10416 >= 0
 makespan_vertex_11: T >= 0
 makespan_vertex_12: T - 10 column_4503 - 10 column_10391 - 10 column_10417
   >= 0
 makespan_vertex_13: T >= 0
 makespan_vertex_14: T - 5 column_1 >= 0
 makespan_vertex_15: T >= 0
 makespan_vertex_16: T >= 0
 makespan_vertex_17: T - 6 column_143 - 6 column_10292 - 6 column_10352
   - 6 column_10353 >= 0
 makespan_vertex_18: T - 6 column_2 - 6 column_10342 - 6 column_10349
   - 6 column_10385 - 6 column_10386 - 6 column_10387 - 6 column_10388
   - 6 column_10389 - 6 column_10390 - 6 column_10391 - 6 column_10418
   >= 0
 makespan_vertex_19: T >= 0
 makespan_vertex_20: T >= 0
 makespan_vertex_21: T >= 0
 makespan_vertex_22: T - 7 column_3 >= 0
 makespan_vertex_23: T - column_4524 - column_4525 - column_10385
   - column_10388 - column_10389 - column_10391 >= 0
 makespan_vertex_24: T - 8 column_4 - 8 column_10342 - 8 column_10349
   - 8 column_10352 - 8 column_10353 >= 0
 makespan_vertex_25: T >= 0
 makespan_vertex_26: T - 9 column_1 - 9 column_4524 - 9 column_4525
   - 9 column_4527 - 9 column_10385 - 9 column_10386 - 9 column_10387
   - 9 column_10388 - 9 column_10389 - 9 column_10390 - 9 column_10391
   >= 0
 makespan_vertex_27: T - 3 column_1482 - 3 column_1483 - 3 column_1484
   - 3 column_1487 - 3 column_1491 - 3 column_10412 - 3 column_10413
   - 3 column_10414 - 3 column_10415 - 3 column_10416 - 3 column_10417
   - 3 column_10418 >= 0
 makespan_vertex_28: T >= 0
 makespan_vertex_29: T - 10 column_2 - 10 column_53 - 10 column_54
   - 10 column_55 - 10 column_4524 - 10 column_4525 - 10 column_4527 >= 0
 makespan_vertex_30: T >= 0
 makespan_vertex_31: T - 11 column_3 - 11 column_93 - 11 column_94
   - 11 column_95 - 11 column_10292 - 11 column_10342 - 11 column_10349
   >= 0
 makespan_vertex_32: T >= 0
 makespan_vertex_33: T - 7 column_4524 - 7 column_4525 - 7 column_4527
   - 7 column_10353 - 7 column_10385 - 7 column_10386 - 7 column_10387
   - 7 column_10388 - 7 column_10389 - 7 column_10390 - 7 column_10391
   >= 0
 makespan_vertex_34: T - 12 column_4 >= 0
 makespan_vertex_35: T >= 0
 makespan_vertex_36: T - 5 column_1433 - 5 column_10352 - 5 column_10353
   - 5 column_10391 - 5 column_10412 - 5 column_10415 - 5 column_10417
   - 5 column_10418 >= 0
 makespan_vertex_37: T - 10 column_10385 - 10 column_10386
   - 10 column_10387 - 10 column_10388 - 10 column_10389 - 10 column_10390
   - 10 column_10413 - 10 column_10414 - 10 column_10416 >= 0
 makespan_vertex_38: T - column_1 - column_10342 - column_10349
   - column_10352 - column_10353 >= 0
 makespan_vertex_39: T >= 0
 makespan_vertex_40: T - 2 column_2 - 2 column_4524 - 2 column_4525
   - 2 column_4527 >= 0
 makespan_vertex_41: T >= 0
 makespan_vertex_42: T - 3 column_3 >= 0
 makespan_vertex_43: T >= 0
 makespan_vertex_44: T - 3 column_4524 - 3 column_10385 - 3 column_10388
   - 3 column_10389 - 3 column_10391 >= 0
 makespan_vertex_45: T - column_1663 - column_4527 - column_10386
   - column_10387 - column_10390 - column_10412 - column_10413
   - column_10414 - column_10415 - column_10416 - column_10417
   - column_10418 >= 0
 makespan_vertex_46: T - 4 column_4 - 4 column_103 - 4 column_104
   - 4 column_105 - 4 column_10385 - 4 column_10386 - 4 column_10387
   - 4 column_10388 - 4 column_10391 - 4 column_10412 - 4 column_10413
   - 4 column_10414 - 4 column_10415 - 4 column_10417 - 4 column_10418
   >= 0
 makespan_vertex_47: T - 5 column_4524 - 5 column_4525 - 5 column_4527
   - 5 column_10389 - 5 column_10390 - 5 column_10416 >= 0
 makespan_vertex_48: T - 5 column_1 >= 0
 makespan_vertex_49: T - 2 column_10292 - 2 column_10342 - 2 column_10349
   - 2 column_10352 - 2 column_10353 - 2 column_10385 - 2 column_10386
   - 2 column_10387 - 2 column_10388 - 2 column_10389 - 2 column_10390
   - 2 column_10391 - 2 column_10412 - 2 column_10413 - 2 column_10414
   - 2 column_10415 - 2 column_10416 - 2 column_10417 - 2 column_10418
   >= 0
 makespan_vertex_50: T >= 0
 makespan_vertex_51: T - 6 column_2 - 6 column_1612 - 6 column_1614
   - 6 column_1615 - 6 column_4524 - 6 column_4525 - 6 column_4527
   - 6 column_10412 - 6 column_10413 - 6 column_10414 - 6 column_10416
   - 6 column_10417 >= 0
 makespan_vertex_52: T >= 0
 makespan_vertex_53: T - 10 column_10292 - 10 column_10352
   - 10 column_10353 - 10 column_10415 - 10 column_10418 >= 0
 makespan_vertex_54: T >= 0
 makespan_vertex_55: T - 7 column_3 - 7 column_1673 - 7 column_1674
   - 7 column_1675 - 7 column_10342 - 7 column_10349 - 7 column_10352 >= 0
 makespan_vertex_56: T - 11 column_4502 - 11 column_4503 - 11 column_4504
   - 11 column_4505 - 11 column_4510 - 11 column_10385 - 11 column_10386
   - 11 column_10387 - 11 column_10388 - 11 column_10389 - 11 column_10390
   - 11 column_10391 >= 0
 makespan_vertex_57: T >= 0
 makespan_vertex_58: T >= 0
 makespan_vertex_59: T - 8 column_4 - 8 column_1452 - 8 column_10292
   - 8 column_10385 - 8 column_10386 - 8 column_10387 - 8 column_10388
   - 8 column_10389 - 8 column_10390 - 8 column_10391 - 8 column_10412
   - 8 column_10413 - 8 column_10414 - 8 column_10415 - 8 column_10416
   - 8 column_10417 - 8 column_10418 >= 0
 makespan_vertex_60: T >= 0
 makespan_vertex_61: T - 11 column_1454 - 11 column_1455 - 11 column_1456
   >= 0
 makespan_vertex_62: T >= 0
 charger_capacity_constraint: column_1 + column_2 + column_3 + column_4
   + column_53 + column_54 + column_55 + column_93 + column_94 + column_95
   + column_103 + column_104 + column_105 + column_143 + column_1422
   + column_1424 + column_1425 + column_1433 + column_1452 + column_1454
   + column_1455 + column_1456 + column_1482 + column_1483 + column_1484
   + column_1487 + column_1491 + column_1612 + column_1614 + column_1615
   + column_1663 + column_1673 + column_1674 + column_1675 + column_4502
   + column_4503 + column_4504 + column_4505 + column_4510 + column_4524
   + column_4525 + column_4527 + column_10292 + column_10342 + column_10349
   + column_10352 + column_10353 + column_10385 + column_10386
   + column_10387 + column_10388 + column_10389 + column_10390
   + column_10391 + column_10412 + column_10413 + column_10414
   + column_10415 + column_10416 + column_10417 + column_10418 <= 4
Bounds
End
