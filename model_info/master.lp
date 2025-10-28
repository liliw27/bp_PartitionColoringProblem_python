\ Model master
\ LP format - for model browsing. Use MPS format to capture full model detail.
Minimize
  1000 column_1 + 1000 column_2 + 1000 column_3 + 1000 column_4
   + 1000 column_5 + 1000 column_6 + 1000 column_7 + 1000 column_8
   + 1000 column_9 + 1000 column_10 + 1000 column_11 + 1000 column_12
   + 1000 column_13 + 1000 column_14 + 1000 column_15 + 1000 column_16
   + 1000 column_17 + 1000 column_18 + 1000 column_19 + 1000 column_20
   + 1000 column_21 + 1000 column_22 + 1000 column_23 + 1000 column_24
   + 1000 column_25 + 1000 column_26 + 1000 column_27 + 1000 column_28
   + 1000 column_29 + 1000 column_30 + column_40 + column_41 + column_42
   + column_43 + column_44 + column_45 + column_46 + column_47 + column_48
   + column_49 + column_50 + column_51 + column_52 + column_53 + column_54
   + column_55 + column_56 + column_59 + column_60 + column_61 + column_63
   + column_64 + column_65 + column_72 + column_73 + column_74 + column_75
   + column_76 + column_77 + column_80 + column_81 + column_82 + column_83
   + column_84 + column_85 + column_86 + column_87 + column_88 + column_89
   + column_90 + column_100 + column_104 + column_106 + column_107
   + column_108 + column_109 + column_110 + column_111 + column_112
   + column_113 + column_114 + column_115 + column_118 + column_119
   + column_120 + column_123 + column_132 + column_133 + column_136
   + column_137 + column_138 + column_140 + column_143 + column_146
   + column_147 + column_153 + column_160 + column_162 + column_164
   + column_165 + column_168 + column_169 + column_170 + column_171
   + column_172 + column_173 + column_174 + column_175 + column_176
   + column_177 + column_178 + column_179 + column_210 + column_211
   + column_212 + column_213 + column_214 + column_215 + column_216
   + column_217 + column_218 + column_220 + column_222 + column_223
   + column_225 + column_226 + column_227 + column_228 + column_229
   + column_230 + column_265 + column_266 + column_267 + column_268
   + column_269 + column_270 + column_271 + column_274 + column_275
   + column_302 + column_303 + column_304 + column_305 + column_306
   + column_307 + column_309 + column_310 + column_311 + column_313
   + column_314 + column_316 + column_317 + column_318 + column_319
   + column_320 + column_321 + column_322 + column_323 + column_324
   + column_325 + column_326 + column_327 + column_346 + column_351
   + column_352 + column_353 + column_354 + column_355 + column_356
   + column_399 + column_400 + column_401 + column_402 + column_403
   + column_404 + column_405 + column_406 + column_407 + column_408
   + column_409 + column_410 + column_412 + column_685 + column_730
   + column_731 + column_732 + column_733 + column_734 + column_735
   + column_736 + column_737 + column_738 + column_739 + column_740
   + column_741 + column_742 + column_743 + column_744 + column_745
   + column_746 + column_747 + column_748 + column_749
Subject To
 each_partition_colored_once_constraint0: column_1 + column_40 + column_45
   + column_81 + column_84 + column_85 + column_86 + column_87 + column_88
   + column_89 + column_90 + column_172 + column_175 + column_179
   + column_213 + column_215 + column_225 + column_226 + column_228
   + column_229 + column_230 + column_269 + column_309 + column_310
   + column_346 + column_355 + column_412 + column_685 + column_741
   + column_744 + column_746 + column_749 >= 1
 each_partition_colored_once_constraint1: column_2 + column_51 + column_52
   + column_53 + column_54 + column_55 + column_56 + column_59 + column_60
   + column_73 + column_76 + column_80 + column_104 + column_109
   + column_110 + column_123 + column_175 + column_230 + column_307
   + column_321 + column_353 + column_355 + column_406 + column_412
   + column_730 + column_731 + column_732 + column_733 + column_734
   + column_735 + column_736 + column_737 + column_738 + column_739
   + column_741 + column_744 + column_746 >= 1
 each_partition_colored_once_constraint2: column_3 + column_104
   + column_106 + column_107 + column_108 + column_109 + column_110
   + column_153 + column_160 + column_170 + column_174 + column_176
   + column_216 + column_265 + column_267 + column_268 + column_269
   + column_274 + column_275 + column_311 + column_316 + column_321
   + column_323 + column_324 + column_325 + column_326 + column_327
   + column_346 + column_351 + column_352 + column_355 + column_402
   + column_404 + column_406 + column_407 + column_409 + column_410
   + column_412 + column_734 + column_737 + column_741 + column_744
   + column_746 >= 1
 each_partition_colored_once_constraint3: column_4 + column_40 + column_77
   + column_100 + column_168 + column_211 + column_302 + column_304
   + column_305 + column_322 + column_742 + column_743 + column_748
   + column_749 >= 1
 each_partition_colored_once_constraint4: column_5 + column_41 + column_42
   + column_43 + column_44 + column_45 + column_46 + column_47 + column_48
   + column_49 + column_50 + column_61 + column_63 + column_64 + column_65
   + column_81 + column_82 + column_83 + column_89 + column_106
   + column_107 + column_108 + column_109 + column_110 + column_143
   + column_146 + column_147 + column_162 + column_164 + column_165
   + column_171 + column_172 + column_173 + column_174 + column_176
   + column_177 + column_178 + column_179 + column_220 + column_223
   + column_225 + column_226 + column_228 + column_229 + column_230
   + column_275 + column_313 + column_317 + column_318 + column_319
   + column_352 + column_355 + column_400 + column_401 + column_402
   + column_403 + column_404 + column_405 + column_408 + column_742
   + column_745 + column_749 >= 1
 each_partition_colored_once_constraint5: column_6 + column_55 + column_56
   + column_61 + column_64 + column_100 + column_106 + column_107
   + column_108 + column_114 + column_115 + column_143 + column_168
   + column_169 + column_172 + column_177 + column_178 + column_210
   + column_211 + column_212 + column_214 + column_216 + column_217
   + column_222 + column_229 + column_266 + column_267 + column_268
   + column_270 + column_271 + column_322 + column_346 + column_351
   + column_352 + column_355 + column_400 + column_401 + column_404
   + column_406 + column_409 + column_744 >= 1
 each_partition_colored_once_constraint6: column_7 + column_41 + column_42
   + column_44 + column_48 + column_51 + column_55 + column_112
   + column_113 + column_123 + column_146 + column_164 + column_165
   + column_171 + column_173 + column_175 + column_210 + column_211
   + column_275 + column_313 + column_317 + column_319 + column_320
   + column_399 + column_403 + column_405 + column_412 + column_746
   + column_747 >= 1
 each_partition_colored_once_constraint7: column_8 + column_111
   + column_112 + column_113 + column_114 + column_115 + column_118
   + column_119 + column_120 + column_162 + column_164 + column_165
   + column_173 + column_175 + column_220 + column_223 + column_226
   + column_227 + column_228 + column_275 + column_303 + column_306
   + column_307 + column_313 + column_314 + column_317 + column_318
   + column_353 + column_354 >= 1
 each_partition_colored_once_constraint8: column_9 + column_41 + column_42
   + column_43 + column_45 + column_47 + column_50 + column_51 + column_55
   + column_59 + column_74 + column_123 + column_133 + column_140
   + column_162 + column_164 + column_165 + column_169 + column_177
   + column_178 + column_179 + column_220 + column_222 + column_223
   + column_225 + column_226 + column_227 + column_228 + column_270
   + column_271 + column_303 + column_306 + column_307 + column_314
   + column_317 + column_354 + column_356 + column_399 + column_403
   + column_408 + column_685 >= 1
 each_partition_colored_once_constraint9: column_10 + column_41 + column_42
   + column_43 + column_44 + column_45 + column_46 + column_47 + column_48
   + column_49 + column_50 + column_72 + column_74 + column_84 + column_123
   + column_136 + column_138 + column_153 + column_212 + column_213
   + column_215 + column_217 + column_222 + column_309 + column_310
   + column_313 + column_316 + column_317 + column_354 + column_356
   + column_406 + column_409 + column_685 + column_740 >= 1
 each_partition_colored_once_constraint10: column_11 + column_43
   + column_45 + column_49 + column_72 + column_74 + column_75 + column_82
   + column_83 + column_88 + column_89 + column_90 + column_107
   + column_108 + column_110 + column_111 + column_114 + column_115
   + column_118 + column_119 + column_120 + column_132 + column_143
   + column_147 + column_169 + column_170 + column_172 + column_176
   + column_177 + column_178 + column_179 + column_215 + column_222
   + column_227 + column_229 + column_314 + column_354 + column_740 >= 1
 each_partition_colored_once_constraint11: column_12 + column_52
   + column_53 + column_59 + column_60 + column_72 + column_73 + column_74
   + column_75 + column_77 + column_118 + column_119 + column_120
   + column_223 + column_314 + column_354 + column_730 + column_731
   + column_732 + column_733 + column_735 + column_736 + column_738
   + column_739 + column_740 + column_743 + column_748 >= 1
 each_partition_colored_once_constraint12: column_13 + column_137
   + column_138 + column_143 + column_146 + column_147 + column_170
   + column_174 + column_176 + column_214 + column_218 + column_265
   + column_267 + column_268 + column_274 + column_324 + column_325
   + column_326 + column_327 + column_346 + column_351 + column_352
   + column_402 + column_405 + column_407 + column_410 + column_734
   + column_742 + column_745 >= 1
 each_partition_colored_once_constraint13: column_14 + column_40
   + column_44 + column_153 + column_174 + column_210 + column_211
   + column_217 + column_313 + column_316 + column_346 + column_409
   + column_730 + column_731 + column_732 + column_733 + column_735
   + column_738 + column_739 + column_743 >= 1
 each_partition_colored_once_constraint14: column_15 + column_46
   + column_81 + column_84 + column_85 + column_86 + column_87 + column_100
   + column_106 + column_112 + column_113 + column_133 + column_136
   + column_137 + column_138 + column_140 + column_153 + column_160
   + column_171 + column_173 + column_218 + column_265 + column_266
   + column_269 + column_270 + column_271 + column_274 + column_309
   + column_310 + column_316 + column_322 + column_323 + column_324
   + column_325 + column_326 + column_327 + column_356 + column_408
   + column_748 >= 1
 each_partition_colored_once_constraint15: column_16 + column_40
   + column_51 + column_52 + column_53 + column_54 + column_55 + column_56
   + column_59 + column_60 + column_104 + column_106 + column_112
   + column_113 + column_118 + column_119 + column_120 + column_123
   + column_175 + column_302 + column_303 + column_304 + column_305
   + column_307 + column_323 + column_351 + column_353 + column_354
   + column_733 + column_739 >= 1
 each_partition_colored_once_constraint16: column_17 + column_53
   + column_85 + column_115 + column_133 + column_153 + column_160
   + column_210 + column_211 + column_212 + column_213 + column_217
   + column_267 + column_270 + column_274 + column_311 + column_316
   + column_318 + column_319 + column_320 + column_352 + column_402
   + column_409 + column_410 + column_730 + column_733 + column_735
   + column_736 + column_738 + column_740 + column_743 + column_748 >= 1
 each_partition_colored_once_constraint17: column_18 + column_87
   + column_113 + column_136 + column_137 + column_138 + column_140
   + column_173 + column_214 + column_216 + column_218 + column_266
   + column_268 + column_271 + column_275 + column_303 + column_306
   + column_309 + column_310 + column_313 + column_316 + column_317
   + column_322 + column_323 + column_324 + column_325 + column_326
   + column_327 + column_356 + column_407 + column_744 + column_746 >= 1
 each_partition_colored_once_constraint18: column_19 + column_82
   + column_90 + column_138 + column_147 + column_153 + column_160
   + column_170 + column_174 + column_176 + column_210 + column_212
   + column_213 + column_214 + column_216 + column_217 + column_218
   + column_220 + column_223 + column_225 + column_227 + column_228
   + column_229 + column_265 + column_266 + column_267 + column_268
   + column_269 + column_274 + column_309 + column_310 + column_311
   + column_323 + column_324 + column_325 + column_346 + column_409
   + column_410 >= 1
 each_partition_colored_once_constraint19: column_20 + column_72
   + column_73 + column_74 + column_75 + column_76 + column_77 + column_80
   + column_111 + column_114 + column_115 + column_132 + column_133
   + column_136 + column_137 + column_138 + column_140 + column_160
   + column_168 + column_169 + column_214 + column_216 + column_218
   + column_222 + column_270 + column_271 + column_356 + column_732 >= 1
 each_partition_colored_once_constraint20: column_21 + column_40
   + column_76 + column_80 + column_88 + column_90 + column_104
   + column_111 + column_132 + column_162 + column_225 + column_226
   + column_304 + column_305 + column_734 + column_737 + column_741
   + column_742 + column_745 + column_749 >= 1
 each_partition_colored_once_constraint21: column_22 + column_41
   + column_42 + column_43 + column_44 + column_45 + column_46 + column_47
   + column_48 + column_49 + column_50 + column_51 + column_54 + column_100
   + column_109 + column_110 + column_123 + column_146 + column_168
   + column_169 + column_170 + column_171 + column_172 + column_174
   + column_176 + column_177 + column_178 + column_179 + column_230
   + column_266 + column_268 + column_309 + column_320 + column_321
   + column_322 + column_399 + column_400 + column_401 + column_404
   + column_407 + column_685 + column_744 + column_746 >= 1
 each_partition_colored_once_constraint22: column_23 + column_63
   + column_65 + column_80 + column_104 + column_109 + column_110
   + column_118 + column_119 + column_120 + column_132 + column_137
   + column_210 + column_211 + column_212 + column_213 + column_215
   + column_217 + column_218 + column_230 + column_265 + column_269
   + column_302 + column_323 + column_324 + column_325 + column_326
   + column_327 + column_353 + column_730 + column_731 + column_733
   + column_736 + column_738 + column_739 + column_740 + column_741
   + column_743 + column_747 >= 1
 each_partition_colored_once_constraint23: column_24 + column_40
   + column_265 + column_269 + column_274 + column_318 + column_319
   + column_320 + column_399 + column_403 + column_730 + column_731
   + column_732 + column_735 + column_743 + column_748 >= 1
 each_partition_colored_once_constraint24: column_25 + column_81
   + column_82 + column_83 + column_84 + column_85 + column_86 + column_87
   + column_88 + column_89 + column_90 + column_111 + column_114
   + column_115 + column_133 + column_136 + column_140 + column_162
   + column_164 + column_165 + column_215 + column_220 + column_225
   + column_226 + column_227 + column_228 + column_229 + column_270
   + column_271 + column_275 + column_306 + column_356 + column_405
   + column_408 + column_745 + column_747 >= 1
 each_partition_colored_once_constraint25: column_26 + column_61
   + column_63 + column_64 + column_65 + column_72 + column_73 + column_74
   + column_75 + column_76 + column_77 + column_80 + column_82 + column_83
   + column_104 + column_107 + column_108 + column_109 + column_120
   + column_132 + column_143 + column_147 + column_168 + column_169
   + column_172 + column_177 + column_178 + column_179 + column_222
   + column_230 + column_267 + column_302 + column_303 + column_304
   + column_305 + column_306 + column_307 + column_311 + column_314
   + column_321 + column_351 + column_353 + column_355 + column_400
   + column_401 + column_404 + column_406 + column_410 + column_685
   + column_741 >= 1
 each_partition_colored_once_constraint26: column_27 + column_133
   + column_140 + column_170 + column_220 + column_223 + column_227
   + column_314 + column_318 + column_319 + column_320 + column_321
   + column_399 + column_403 + column_407 + column_408 >= 1
 each_partition_colored_once_constraint27: column_28 + column_162
   + column_164 + column_165 + column_175 + column_302 + column_303
   + column_304 + column_305 + column_306 + column_307 + column_311
   + column_353 + column_402 + column_405 + column_410 + column_412
   + column_734 + column_737 + column_742 + column_745 + column_747
   + column_749 >= 1
 each_partition_colored_once_constraint28: column_29 + column_81
   + column_82 + column_83 + column_84 + column_85 + column_86 + column_87
   + column_88 + column_89 + column_90 + column_107 + column_108
   + column_136 + column_143 + column_146 + column_147 + column_160
   + column_212 + column_213 + column_214 + column_215 + column_216
   + column_310 + column_311 + column_352 + column_402 + column_736
   + column_737 + column_740 + column_747 >= 1
 each_partition_colored_once_constraint29: column_30 + column_40
   + column_61 + column_63 + column_64 + column_65 + column_100
   + column_112 + column_113 + column_132 + column_137 + column_168
   + column_171 + column_173 + column_175 + column_266 + column_305
   + column_322 + column_326 + column_327 + column_400 + column_401
   + column_412 >= 1
Bounds
End
