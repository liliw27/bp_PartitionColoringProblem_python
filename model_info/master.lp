\ Model master
\ LP format - for model browsing. Use MPS format to capture full model detail.
Minimize
  column_31 + column_32 + column_33 + column_34 + column_35 + column_36
   + column_37 + column_38 + column_39 + column_40 + column_41 + column_42
   + column_43 + column_44 + column_45
Subject To
 each_partition_colored_once_constraint0: column_31 + column_45 >= 1
 each_partition_colored_once_constraint1: column_32 + column_33 + column_41
   + column_42 + column_43 + column_44 >= 1
 each_partition_colored_once_constraint2: column_34 + column_35 + column_41
   + column_43 + column_44 + column_45 >= 1
 each_partition_colored_once_constraint3: column_36 + column_42 >= 1
 each_partition_colored_once_constraint4: column_37 + column_38 + column_39
   + column_40 + column_41 + column_42 + column_43 + column_44 + column_45
   >= 1
Bounds
End
