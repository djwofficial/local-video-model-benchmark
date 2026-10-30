# LTX-2.5 fresh runs: one video per process

Each video is its own process (loads the text encoder and models), as the Mac-mini script does. Peak = process lifetime phys_footprint.

|Prompt|Seed|Seconds (incl. loading)|Peak GiB|
|---|---:|---:|---:|
|redball|42|196.9|15.45|
|redball|43|199.5|15.47|
|redball|44|193.6|15.45|
|redball|average|196.7|15.46|
|bluecar|42|188.2|15.46|
|bluecar|43|197.0|15.46|
|bluecar|44|190.5|15.48|
|bluecar|average|191.9|15.47|
