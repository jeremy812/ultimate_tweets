#!flask/bin/python
import boto3
import datetime
import json
import random
import re
import time

import urllib

import operator as op


from boto3.dynamodb.conditions import Attr
from boto3.dynamodb.conditions import Key
from collections import defaultdict
from collections import namedtuple
from dateutil.parser import parse
from flask import Flask
from flask import Response
from flask import jsonify
from flask import render_template
from flask import request
from functools import reduce
from math import exp

from random import choice
dynamo = boto3.resource('dynamodb', region_name='us-east-1')
'''Dealing with ratings and score'''

tzs = {"AL": "-0600", "AK": "-1000", "AZ": "-0700", "AR": "-0600", "CA": "-0800", "CO": "-0700", "CT": "-0500", "DE": "-0500", "FL": "-0600", "GA": "-0500", "HI": "-1000", "ID": "-0800", "IL": "-0600", "IN": "-0600", "IA": "-0600", "KS": "-0700", "KY": "-0600", "LA": "-0600", "ME": "-0500", "MD": "-0500", "MA": "-0500", "MI": "-0600", "MN": "-0600", "MS": "-0600", "MO": "-0600",
       "MT": "-0700", "NE": "-0700", "NV": "-0800", "NH": "-0500", "NJ": "-0500", "NM": "-0700", "NY": "-0500", "NC": "-0500", "ND": "-0700", "OH": "-0500", "OK": "-0600", "OR": "-0800", "PA": "-0500", "RI": "-0500", "SC": "-0500", "SD": "-0700", "TN": "-0600", "TX": "-0700", "UT": "-0700", "VT": "-0500", "VA": "-0500", "WA": "-0800", "WV": "-0500", "WI": "-0600", "WY": "-0700"}
ratings = {"Colorado State B": 746.0054577840323, "Grand Canyon": 907.8923483349979, "Brigham Young B": 634.3113697918914, "Denver": 831.2762374495085, "New Mexico": 1179.405884350516, "Alabama": 1540.1405009942812, "Vanderbilt": 1032.1540470633997, "Illinois State": 1140.7596540546638, "Auburn": 1624.4115893583005, "Alabama-Huntsville": 1346.5355791586362, "Illinois State B": 624.8764160833615, "Alabama B": 592.058752660771, "Kentucky B": 329.6319326026101, "Temple": 1367.6822913802737, "South Florida": 1132.1423969791856, "Cincinnati": 1371.8083319650152, "Texas-Dallas": 1585.116529192736, "Pittsburgh": 2023.78279102547, "Virginia Tech": 1475.636840988251, "Northwestern B": 443.73938386728486, "South Florida B": 131.91661758881713, "Embry-Riddle (Florida)": 728.4082020096142, "Florida Tech B": 174.71260354226106, "Stetson": 378.7169645275643, "Brown": 2064.4891226757118, "Central Florida": 1827.8902960676103, "Carleton College-CUT": 1960.644148629781, "Illinois": 1562.0249188380058, "Kentucky": 1088.5027410733637, "Alabama-Birmingham": 912.6497803623486, "Georgia State": 1196.1109888035103, "Minnesota": 1795.2459782716421, "Harvard": 1510.7185770313954, "Northeastern": 1604.3793551761535, "Texas": 1834.5880110908413, "Georgia": 1657.0907920673478, "Cornell": 1073.2159275849338, "Wisconsin": 1861.868071392582, "Tufts": 1737.0750280670568, "Texas A&M": 1584.1848414491892, "Michigan": 1739.4746770509748, "Washington B": 736.3885413922897, "Gonzaga": 840.2161151593704, "Washington C": 457.77104495412976, "Drexel": 1031.4549449424253, "Virginia Commonwealth": 1010.0355549063524, "North Carolina B": 1119.4188959120722, "Mary Washington": 1291.5954319513087, "Vermont": 1551.181770159605, "Williams": 1195.5275046344113, "RIT": 956.9951375672364, "NYU": 913.4128352530463, "SUNY-Binghamton": 1008.9180555598543, "Liberty": 1223.167009602094, "Pennsylvania": 1097.4671542320477, "South Carolina": 1644.9154746851593, "Arizona State B": 887.1803470884553, "Northern Arizona": 947.3209490642928, "Washington State": 983.948041299823, "Pacific Lutheran": 616.5197039536085, "Lewis & Clark": 1215.2487657766355, "Florida B": 855.2525728795893, "Rutgers": 1281.4486654096738, "Brigham Young": 1967.3106627701006, "LSU": 1537.2908432727052, "Mississippi State": 1021.4010953775984, "Florida Tech": 856.6437175415858, "Columbus State": 10.182474360197435, "Georgia Southern": 971.4643861212672, "Miami": 423.9139122099449, "North Carolina": 2049.5219139548635, "Duke": 1420.862982945494, "Richmond": 1343.7386674595139, "Carleton College-GoP": 1332.0134479188894, "Clemson": 1148.9728096214424, "Appalachian State": 1270.9051559153409, "Georgia Tech": 1278.7547367774098, "Tennessee": 1390.220776191163, "North Carolina-Wilmington": 1612.6728774611865, "Georgetown": 1201.5555124646958, "Notre Dame": 1480.3261887935728, "Indiana": 1419.3462290489945, "Michigan B": 1084.881834087862, "Pittsburgh B": 1119.1047164053057, "Victoria": 1564.5044332800999, "Southern California": 1848.0897684133902, "Cal Poly-SLO": 1972.2558439066752, "Stanford": 1491.0591121282807, "Florida": 1385.6414008709316, "Northwestern": 1498.9513525702998, "Florida State": 1458.1268806324938, "Bethel": 748.2856831484274, "Minnesota C": 412.75242449012813, "Macalester": 961.5000427082966, "Winona State": 981.49214853295, "Carleton Hot Karls": 635.2611772534112, "Minnesota B": 1072.1330265031918, "Puget Sound": 1158.235120490744, "Oklahoma": 1295.1461759356646, "Boston College": 1108.7154746335314, "Case Western Reserve": 1247.3207189196232, "William & Mary": 1610.3958061007243, "California-San Diego": 1442.7010804736847, "California-Santa Barbara": 1484.9569348940329, "Dartmouth": 1554.8781209728838, "Oregon": 2026.6880400968462, "Utah": 1346.7365455007287, "Colorado State": 1734.7076698627807, "North Carolina State": 1877.7711458242043, "Emory": 1342.5581764680392, "Carnegie Mellon": 1412.6921328059527, "Washington": 1868.3520583332115, "California": 1686.4839906310092, "Mississippi": 584.0493696412105, "Penn State": 1407.6714393634288, "Maryland": 1507.3203436542221, "Massachusetts": 1905.295716989896, "Tulane": 1303.3489383864523, "UCLA": 1568.2372503892097, "Santa Clara": 1248.4167673323439, "California-Davis": 1235.9151234719782, "British Columbia": 1537.8371451639516, "Northern Iowa": 798.180620802035, "Southern Illinois-Edwardsville": 431.25871246726484, "Missouri": 825.4209177109412, "Texas Christian": 923.1510705282262, "Wisconsin-Whitewater": 1191.8331220281455, "Texas Tech": 1636.0083515893168, "Colorado": 1936.7301421916604, "Nevada-Reno": 1187.9598832413346, "Oregon State": 1406.1370061319944, "Whitman": 1418.312925195482, "Boston College B": 804.9122568550906, "Central Florida B": 425.05711357052064, "Baylor": 1185.1536969517738, "Nebraska": 946.8866578253605, "North Texas": 920.3131522045749, "John Brown": 1216.4795638713206, "Davidson": 1223.6524747763501, "Minnesota-Duluth": 1078.3743170102966, "North Carolina-Asheville": 1085.6912789003293, "Arizona B": 279.2144725034831, "Air Force B": 344.4253403413364, "Virginia": 1505.337713032997, "Chicago": 1117.0587724083734, "Michigan State": 863.4238423778008, "Arizona": 1450.7646066410127, "George Washington": 956.6113845811957, "St Olaf": 1308.2616448758524, "Brandeis": 1317.026057297699, "Missouri S&T": 1122.6502884277058, "Ohio Northern": 518.5644612259433, "Michigan Tech": 1310.947281463647, "Portland": 1194.5424242179447, "Grinnell": 519.4977020484056, "North Park": 684.188274333452, "Indiana Wesleyan": 415.3626666422414, "California-Santa Cruz": 1241.1815502422314, "Union (Tennessee)": 759.3566253386991, "Texas-El Paso": 283.7971429798963, "Georgia College": 977.0311065056073, "Middlebury": 1588.1345308409925, "Air Force": 1359.127553788574, "Montana State": 980.34206288166, "Humboldt State": 933.7079032530079, "Whitworth": 933.3974239693702, "Utah State": 1159.8175389222586, "Wisconsin B": 879.3947586556111, "Wisconsin-Eau Claire": 825.3339729466164, "Wisconsin- La Crosse": 897.4152482029159, "Lewis & Clark B": 221.4842655302519, "Elon": 1040.7329864883732, "Campbell": 535.7745335497705, "Florida Atlantic": 633.6683193563113, "Luther": 1229.1322112109756, "Wisconsin-Platteville": 893.6131594452063, "Indiana B": 573.4518274922965, "Ohio": 1390.2899269075288, "George Mason": 835.1284903901992, "Western Washington B": 478.3983520654978, "Yale": 1117.001480850322, "MIT": 1138.3088254853271, "Brown B": 830.8541134758591, "Colby": 1337.3938017449707, "Bates College": 1234.387836476293, "Yale B": 96.11282244567695, "Rutgers B": 319.0385134330697, "Princeton": 1088.6902246403693, "Maryland-Baltimore County": 774.4339659393852, "Shippensburg": 825.0150862286898, "Lehigh": 1036.4441408285118, "Towson": 594.9311419680133, "American": 457.4613459993428, "Cedarville": 966.3296256234913, "Wake Forest": 544.5223945959193, "Christopher Newport": 787.4817230392474, "Susquehanna": 239.59634742829448, "Lehigh B": -211.15554167997692, "Princeton B": 307.1860366052528, "Colorado College": 1026.993672928088, "Rice": 1342.7858996916427, "Arkansas": 990.362465159787, "Texas State": 1274.761437937614, "Kansas": 1147.6400757634372, "Illinois-Chicago": 439.7225026563601, "Wisconsin-Stout": 182.17740456870254, "Grand Valley State": 1218.9802235197387, "Wheaton (Illinois)": 876.8159743723713, "Coe": 223.0312689024685, "Milwaukee School of Engineering": 564.1749352473947, "Cal Poly-SLO B": 667.8904295309422, "Caltech": 499.20192999414706, "Arizona State": 863.3405299906515, "Chico State": 983.0519791651544, "UCLA B": 436.3554940160542, "Southern California B": -92.01060074652445,
           "California-San Diego B": 425.2519961738907, "Cal Poly-Pomona": 831.0089065115466, "California-Irvine": 447.06052106020536, "Johns Hopkins": 1585.6649089845314, "SUNY-Stony Brook": 994.6665698009471, "Syracuse": 1096.6582600412405, "Ohio State": 1833.7779492565073, "Purdue": 1560.5393041914301, "James Madison": 1124.7019783991693, "Dayton": 1028.33664578326, "Wisconsin-Milwaukee": 1191.274266495937, "Texas-San Antonio": 573.1360159568758, "Truman State": 1199.9121720175167, "San Jose State": 526.561222242566, "Ithaca": 686.6893642579067, "Skidmore": 649.1466739005109, "Bowdoin": 1226.2579505260328, "Rensselaer Polytech": 811.0540044423266, "Rochester": 858.5016750062659, "Maine": 1089.9768581523876, "California-Irvine B": -150.78520640705707, "Claremont": 848.2887598940744, "Sacramento State": 580.6422901111237, "Saint Louis": 1082.3833661717958, "Iowa": 1184.1710766048116, "Marquette": 1244.442838509001, "High Point": 677.1690240383472, "Florida Gulf Coast": 725.8143511211248, "Stephen F. Austin": 630.2169253065113, "Southern Methodist": 457.9258688037439, "Oklahoma State": 1351.7632906337537, "Kansas State": 1005.4695436789742, "Anderson": 778.156944223627, "Berry": 970.6204326387959, "Texas B": 461.6884655039229, "Seattle": 417.06294868346487, "Marquette B": 387.10898576805573, "St. Thomas": 842.3566085921647, "Drake": 633.1634498069278, "Illinois B": 700.6505643499318, "Purdue B": 773.6338641320554, "Texas-Dallas B": 224.48842586138932, "Sonoma State": 527.1587732608939, "Occidental": 834.4852410736419, "Montana": 883.5442192407635, "Temple B": 149.5535404568789, "College of New Jersey": 479.03245309696445, "Belmont": 955.2523993068585, "Georgia Tech B": 852.7605724453925, "SUNY-Buffalo B": 24.305967570560362, "West Virginia": 458.8044070887906, "Case Western Reserve B": 295.8307932194984, "Siena": 320.9597482842237, "Washington University": 1155.702706749445, "Iowa State": 1497.5976639813161, "Minnesota State-Mankato": 975.7482289440343, "Wright State": 432.10081127265977, "Kenyon": 497.7972881500608, "Pacific Lutheran B": 19.54861342341091, "West Chester": 887.9488226016452, "Boston University": 1145.9090679121668, "Army": 960.5449791758505, "Dickinson": 461.41055958750536, "SUNY-Buffalo": 851.5730401811987, "Colorado School of Mines": 1156.0646697539921, "Wisconsin C": 540.869454026798, "Toledo": 641.2703154400822, "Trinity": 737.1321383145904, "Connecticut": 1219.4387132681168, "Navy": 647.1440841673201, "East Carolina": 932.117698889424, "Franciscan": 1231.3214346694078, "Xavier": 776.2002104937773, "DePaul": 834.9153469045277, "California B": 934.8917808910171, "SUNY-Albany": 976.5474205773836, "Stevens Tech": 780.2215680677842, "Olivet Nazarene": 768.3028360983534, "Valparaiso": 909.8872511257202, "Tufts B": 686.2450319892554, "Rowan": 753.3630059121735, "Marist": 1134.0269687982268, "Hofstra": 577.8663156938148, "Columbia": 778.8945280044567, "Cornell B": 290.8832511764972, "New Hampshire": 1138.7422379336801, "Tennessee-Chattanooga": 1226.8201093507703, "Oberlin": 954.6057622093393, "Rose-Hulman": 591.0471081064469, "Idaho": 693.3411962462162, "Charleston": 789.6741990729125, "Massachusetts-Lowell": 598.8287048934268, "Worcester Polytech": 460.04188622720386, "Vanderbilt University  B": 332.7731381043991, "Middle Tennessee State": 942.3471309429831, "Haverford": 805.5938929369441, "St John's": 731.4943272994577, "Georgia B": 766.2685708846695, "Michigan State B": 425.22826662436887, "Northern Illinois": 500.9869949681987, "Samford": 721.1729517967831, "Delaware B": 659.8967321222511, "SUNY-Fredonia": 654.9000548603458, "North Carolina State  B": 560.0841210052356, "Knox": 827.8778137186395, "Messiah": 1040.6916942156631, "Maryland B": 829.5085136576804, "Pennsylvania B": 440.8052587536457, "Georgetown B": 170.02180884227943, "Shenandoah": 414.3320771412905, "Sul Ross State": 861.8608956466651, "Texas State  B": 304.50038706135587, "Tulsa": 305.4834614241858, "Central Arkansas": 124.82002065671642, "American B": 30.152770190690394, "George Washington B": 432.10814085928405, "Virginia B": 403.2033555283786, "Texas A&M B": 271.0692123578336, "Loyola-Chicago": 818.8788953656118, "Arkansas State": 525.8477967272241, "Colorado School of Mines - B": 299.25848124777104, "Delaware": 1042.4348164554747, "North Carolina-Charlotte": 1171.470105163385, "SUNY-Geneseo": 1007.1029074784359, "Villanova": 1127.4100983953879, "Virginia Tech B": 643.1302552077664, "Denison": 366.08724288324254, "Oberlin B": 15.44398430615084, "Kent State": 667.0126508860303, "Salisbury": 603.1924606439428, "Penn State B": 769.5901564767806, "Rhode Island": 588.1389884380849, "Carthage College": 229.80742055391707, "Colorado B": 759.5968745888639, "Indiana (Pennsylvania)": 175.3625177556743, "Akron": 756.9402842910814, "Wisconsin-Oshkosh": 380.8038754030808, "Colorado-Denver": 1006.2545550583492, "Eastern Illinois": 149.2673546390714, "Bradley": 899.8325399291547, "Amherst College": 781.9653253525964, "Miami (Ohio)": 868.2835154752051, "Colorado-Colorado Springs": 484.79273001923286, "Carnegie Mellon B": 479.1897813829644, "Bentley": 942.7846777445025, "Texas-Arlington": 304.61676393008463, "Dallas": 283.8469597596346, "SUNY-Cortland": 703.8046394556487, "Kennesaw State": 1556.1972496670694, "Maryland-Baltimore County B": 277.08537646679554, "Cleveland State": 444.1362655951442, "Ball State": 708.1236467287338, "Tennessee Tech": 675.1212784124433, "Swarthmore": 843.3147672349501, "Iowa State B": 549.1345907452054, "Western Michigan": 405.8686647535922, "Northern Michigan": 262.5307822321558, "Kettering": 94.33510584993432, "Colgate": 863.4790134697234, "Lamar": 622.217847367971, "Abilene Christian": 448.7318402937003, "Bryant University": 1249.2856268410471, "William & Mary B": 517.248389062518, "South Carolina B": 805.9403900555071, "James Madison B": 517.1914779108425, "Vermont B": 306.36866988829655, "Ursinus": -434.27458122933905, "Colorado Mesa": 610.111427519868, "Jefferson": 215.075284947782, "Providence College": 501.3665588063747, "Lancaster Bible": -169.01535176081165, "St Mary's (Maryland)": 46.55623922594302, "Sacred Heart": 86.5302384475029, "Muhlenberg": 546.6468164399224, "Cornell College": 314.02399481408787, "Creighton": 529.0980156573324, "Northwestern-St. Paul": 258.64756434902506, "Millersville": 358.9195267995801, "Catholic": 692.4453148979017, "SUNY-Stony Brook B": 54.58307080251991, "Northeastern C": 518.4186253731051, "Southern Connecticut State": 469.90962946904256, "Massachusetts Amherst B": 764.4727365119969, "Southern Indiana": 319.26063770786885, "Dartmouth B": 636.1576002511274, "San Diego State": 679.3483721205746, "Connecticut B": 654.1128391707593, "Villanova B": 419.81007667169604, "North Georgia": 890.8413826402387, "Notre Dame B": 413.2259236248309, "Wentworth": 620.9058399054422, "Cal State-Long Beach": 798.3732483877844, "Trine": 357.1138666888147, "SUNY-Oneonta": 739.6378961606098, "SUNY Oneonta B": -118.06880260610997, "Jacksonville State": 1333.1794493112968, "Stonehill": 828.5747729935093, "John Carroll": 258.3669334431094, "New Jersey Tech": 389.08288387725446, "Franklin & Marshall": 161.27576701514369, "Butler": 944.8493642024523, "Massachusetts C": 971.8478117907678, "Saint Joseph's": 46.086332937039934, "Rhode Island B": -339.98916499902293, "Ottawa (Arizona)": -475.4182239326376, "Amherst College B": -186.713250642144, "West Chester B": 9.202224057475576, "Northeastern B": 799.2169060173826, "Fairfield": 244.05158057039162, "Wesleyan": 1047.6337553566502, "Allegheny": 385.7703529307982, "SUNY-Cortland B": -79.62901366900746}
handles = {"Northern Iowa": "UNIUltimate", "North Carolina": "UNC_Darkside", "Brown": "BMoUltimate", "Pittsburgh": "Pittultimate", "Oregon": "egotime", "Cal Poly-SLO": "CORE_ultimate", "Brigham Young": "BYUCHIUltimate", "Carleton College-CUT": "cutrules", "Colorado": "CUMamabird", "Massachusetts": "UMassUltimateM", "Washington": "sundodgers", "North Carolina State": "wolfpackultim8", "Wisconsin": "hodaglove", "Texas": "texas__tuff", "Ohio State": "pbultimate", "Southern California": "uscmensultimate", "Central Florida": "PupsofConflict", "Minnesota": "1Duck1Love", "Michigan": "magnUMultimate", "Tufts": "tufts_emen", "California": "CalUGMO", "Georgia": "JojahUltimate", "South Carolina": "USC_Ultimate", "Texas Tech": "techtumbleweed", "Auburn": "AuburnUltimate", "North Carolina-Wilmington": "seamenultimate", "Northeastern": "NUMensUltimate", "William & Mary": "wmultimate", "Texas A&M": "DozenUltimate", "Texas-Dallas": "utd_ultimate", "Middlebury": "pranksters69", "Victoria": "uvictimultimate", "Johns Hopkins": "dangerzoneulti", "Alabama": "bama_ultimate", "Illinois": "IlliniMensUlti", "UCLA": "uclaultimate", "Vermont": "team_chill", "Purdue": "UndueUltimate", "Dartmouth": "DMouthPainTrain", "LSU": "LSUUltimateM", "Harvard": "HarvardRedLine", "Virginia": "nighttrainatuva", "Maryland": "spacebastards", "Northwestern": "NUTUltimate", "Iowa State": "UltimateISU", "Stanford": "stanfordblood", "California-Santa Barbara": "UCSB_Ultimate", "Indiana": "Hoosier_Mamas", "Notre Dame": "ndultimate", "Virginia Tech": "VTBurn", "Whitman": "MWhitman_Sweets", "Florida State": "DUFtrainroll", "Oregon State": "OSU_ultimate", "Arizona": "SunburnUltimate", "Ohio": "OUultimate", "Carnegie Mellon": "mryukultimate", "Duke": "Duke_Brimstone", "Penn State": "spank_ultimate", "Tennessee": "TennUltimateM", "Oklahoma State": "OstateUltimato", "Cincinnati": "UCUltimate", "Rice": "riceultimate", "Florida": "FloridaUltimate", "Temple": "templeultimate", "Emory": "EmoryJuice", "Air Force": "AFU_Afterburn", "Alabama-Huntsville": "uahultimate", "Michigan Tech": "DiscoTechUlti", "Utah": "ZCU_Ultimate", "Richmond": "urspidermonkeys", "Carleton College-GoP": "goprocks", "Tulane": "TUultimate", "Oklahoma": "wrathfulapes", "Georgia Tech": "gttribe", "Brandeis": "brandeistron", "Marquette": "BirdhouseMU", "Santa Clara": "SCABUltiFris", "Appalachian State": "Nomads_Ultimate", "Tennessee-Chattanooga": "UTCSwamp", "Luther": "lutherultimate", "John Brown": "JBUIronfist", "Iowa": "UofIowaUltimate", "Connecticut": "UConnGrind", "Georgetown": "GeorgetownUlti", "Liberty": "LUmensUltimate", "Lewis & Clark": "BacchusUltimate", "California-Santa Cruz": "slugultimate", "Franciscan": "FranciscanFATAL", "Davidson": "DUFF_Cats", "Georgia State": "GSUnderground", "Truman State": "JujiTSUltimate", "New Mexico": "HantaVirus_Ulti", "Williams": "wufoultimate", "Washington University": "wucontra", "Nevada-Reno": "nevadaultimate", "Illinois State": "isugnomes", "Wisconsin-Milwaukee": "BlaCkatUltimate", "Villanova": "VUMainLine", "Puget Sound": "upsultimate", "Wisconsin-Whitewater": "subparUWW", "MIT": "MITultimate", "Baylor": "BaylorUltimate", "New Hampshire": "unhultimate", "James Madison": "hellfishulti", "Utah State": "usult_imate", "Yale": "yalesuperfly", "Pittsburgh-B": "pittb_ultimateM",
           "Boston College": "bcultimate", "Chicago": "UChiUltimate", "North Carolina-B": "unc_batch", "Kentucky": "KYUltimate", "Missouri S&T": "miner_threat", "Pennsylvania": "VoidUltimate", "South Florida": "usfultimate", "Cornell": "BudsUltimate", "Princeton": "clockworkultima", "Syracuse": "doomultimate", "Michigan-B": "Reserve2K19", "North Carolina-Asheville": "UNCAshUltimate", "Dayton": "UDUltimate", "Elon": "Elon_BigFatBomb", "Drexel": "DrexelUltimate", "Lehigh": "lehighultimate", "Minnesota-B": "UglyDucklingUMN", "Mississippi State": "HailStateUlt", "Messiah": "messiahultimate", "SUNY-Geneseo": "geneseoultimate", "Georgia Southern": "GASo_Ultimate", "Washington State": "WSU_Ultimate", "RIT": "spudheds", "Georgia College": "gc_ultimate", "George Washington": "Gdub_Ultimate", "Montana State": "RumRunnersMT", "Cedarville": "cedarvilleuf", "Winona State": "WSUExperience", "Bentley": "bentleyultimate", "Army": "AWPUltimate", "Nebraska": "cornfedultimate", "East Carolina": "ECUUltimate", "Whitworth": "Whitworth_Ulti", "Northern Arizona": "ElPonderosoNAU", "NYU": "NYUpurplehaze", "Middle Tennessee State": "mtsuultimate", "Arizona State": "ASU_Ultimate", "North Texas": "UltimateUnt", "Grand Canyon": "GCUUltimate", "Colgate": "jabberwockult", "Rochester": "piggiesultimate", "Valparaiso": "ValpoUltimate", "Wisconsin-Platteville": "udderburn", "George Mason": "MasonUltimate", "SUNY-Buffalo": "gehultimate", "Wisconsin-B": "wheatonmastodon", "Shippensburg": "ShipUltimate", "Wisconsin- La Crosse": "ultimateluc", "DePaul": "depaultimate", "Michigan State": "MSUARCUltimate", "Swarthmore": "WormsUltimate", "Rensselaer Polytech": "rpitrudge", "Cal Poly-Pomona": "cowultimate", "Wisconsin-Eau Claire": "eauzoneultimate", "Haverford": "donkeyultimate", "Xavier": "BLOB_ultimate", "Maryland-B": "umdfub", "Texas Christian": "HighNoonTCU", "Samford": "su_ultimate", "Georgia-B": "Chillydwags", "Delaware-B": "sideshow_b", "Colorado State-B": "csuhibida_b", "Olivet Nazarene": "blackp3nguins", "St John's": "SJUultimate", "Illinois-B": "boomlandulti", "SUNY-Fredonia": "fredoniault", "Bethel": "BethelUltimate", "High Point": "hpu_ultimate", "Navy": "navyultimate", "North Park": "NPLostBoys", "Wentworth": "WITUltimate", "Towson": "tupandamonium", "Hofstra": "HUFDUltimate", "Illinois State-B": "isugnomes", "Rhode Island": "mensriut", "Pacific Lutheran": "ReignMenPLU", "Rose-Hulman": "rhitultimate", "Alabama-B": "bama_ultimate", "Carleton Hot Karls": "HotKarlsAreOK", "Ohio Northern": "ONUDarkside", "Drake": "Drake_Ultimate", "Wake Forest": "WFUltimate", "William & Mary-B": "wm_seahorse", "Kenyon": "kenyonserf", "Arkansas State": "redwolfultimate", "Northern Illinois": "NIUWolfpack", "Western Washington-B": "mudwwu", "California-Irvine": "irvineultimate", "Dickinson": "jfturks", "American": "AU_Ultimate", "Miami": "UMiamiUltimate", "Northwestern-B": "BoltUltimate", "Pennsylvania-B": "None,Ultimate", "Western Michigan": "DarkHorseUlt", "Central Florida-B": "UCF_Havoc", "Wisconsin-Oshkosh": "OshkoshUltimate", "Illinois-Chicago": "UIC_Utimate", "Indiana Wesleyan": "IWU_Ultimate", "Case Western Reserve-B": "FightingGobies", "Kentucky-B": "KYUltimate",  "Georgetown-B": "GeorgetownUltiB", "South Florida-B": "USFScourge", "Coe": "kohucksultimate", "Southern California-B": "uscmensultimate"}


class UsaUltimate:
    def __init__(self, dynamo, cache=[]):
        self.table = dynamo.Table('usau')
        self.cache = cache

    def get(self, team, start=None, end=None):

        if start is None:
            start = int((datetime.datetime.now() -
                         datetime.timedelta(hours=3)).timestamp())
        if end is None:
            end = int(datetime.datetime.now().timestamp())
        fe = Key('timestamp').between(start, end) and Attr('id').contains(team)
        response = self.table.scan(
            FilterExpression=fe
        )
        for item in response['Items']:
            item['timestamp'] = int(item['timestamp'])
            yield item

        while "LastEvaluatedKey" in response:

            response = self.table.scan(
                FilterExpression=fe,
                ExclusiveStartKey=response['LastEvaluatedKey']
            )
            for item in response['Items']:
                item['timestamp'] = int(item['timestamp'])
                yield item


class Twitter():
    def __init__(self, dynamo):
        self.table = dynamo.Table('twitter')
        self.cache = defaultdict(list)

    def get(self, handle, start=None, end=None):
        if start is None:
            start = int((datetime.datetime.now() -
                         datetime.timedelta(hours=3)).timestamp())
        if end is None:
            end = int(datetime.datetime.now().timestamp())

        try:
            return self.get_from_dynamo(handle, start, end)
        except Exception as e:
            print(e)
            return []

    def get_from_dynamo(self, handle, start, end):
        print(handle, start, end)
        fe = Key("handle").eq(handle) & Key('timestamp').between(start, end)
        rv = []
        response = self.table.query(
            KeyConditionExpression=fe
        )

        rv.extend(response['Items'])
        while "LastEvaluatedKey" in response:
            response = self.table.query(
                KeyConditionExpression=fe,
                ExclusiveStartKey=response['LastEvaluatedKey']
            )
            rv.extend(response['Items'])
        return rv


twitter_client = Twitter(dynamo)
usau_client = UsaUltimate(dynamo)


''' Didn't know of any closed form for going backwards from probability of winning a game to 13 to probability of winning each point,
 so I just calculated this forward and made a map which we will then reverse. 
 bounding that to never have probability of winning a point >70%/<30% because differences there dont actually impact probabiltiy of winning (it is guaranteed already)'''

point_probability = {"0.0": 0.0, "4.649673552843914e-20": 0.01, "3.4023244415274392e-16": 0.02, "5.90864396050234e-14": 0.03, "2.2170351002424726e-12": 0.04, "3.591139402335667e-11": 0.05, "3.417898270932817e-10": 0.06, "2.2530554457400263e-09": 0.07, "1.134744360785885e-08": 0.08, "4.6519009637624665e-08": 0.09, "1.620834160186066e-07": 0.1, "4.950026727609375e-07": 0.11, "1.3555586067281205e-06": 0.12, "3.3866673670714235e-06": 0.13, "7.823472917626568e-06": 0.14, "1.688957575833256e-05": 0.15, "3.43678384230481e-05": 0.16, "6.638087222219781e-05": 0.17, "0.0001224080903952189": 0.18, "0.00021655216427113292": 0.19, "0.00036904803455582497": 0.2, "0.0006079831981233746": 0.21, "0.0009711703705926249": 0.22, "0.001508084943015217": 0.23, "0.002281752431827442": 0.24, "0.0033704480688667715": 0.25, "0.004869054429982761": 0.26, "0.0068899158772198574": 0.27, "0.009563032364633513": 0.28, "0.013035450869251647": 0.29, "0.017469740525972943": 0.3, "0.0230414767062095": 0.31, "0.029935708102128866": 0.32, "0.03834243684254913": 0.33, "0.04845120156931692": 0.34, "0.06044491356302378": 0.35, "0.07449315251203627": 0.36, "0.09074517749475265": 0.37, "0.10932294662635365": 0.38, "0.1303144626055361": 0.39, "0.15376776886317295": 0.4, "0.17968591089379493": 0.41, "0.20802314943067163": 0.42, "0.23868266729101317": 0.43, "0.2715159519175414": 0.44, "0.3063239637849797": 0.45, "0.3428601206283962": 0.46, "0.38083504316554473": 0.47,
                     "0.4199229242295303": 0.48, "0.45976930464697596": 0.49, "0.4999999701976776": 0.5, "0.5402306284745048": 0.51, "0.5800769855816968": 0.52, "0.6191648225815238": 0.53, "0.6571396715647941": 0.54, "0.6936757111761186": 0.55, "0.7284835402211797": 0.56, "0.7613165433958287": 0.57, "0.7919756320406687": 0.58, "0.8203122212268322": 0.59, "0.8462293879954339": 0.6, "0.8696812395379047": 0.61, "0.8906705998881373": 0.62, "0.9092451949845791": 0.63, "0.9254925750029538": 0.64, "0.9395340566923633": 0.65, "0.9515179950476776": 0.66, "0.9616127020411225": 0.67, "0.9699993204087859": 0.68, "0.9768649337631357": 0.69, "0.9823961526119759": 0.7, "0.9867733619724816": 0.71, "0.9901657534437358": 0.72, "0.9927271963453259": 0.73, "0.994592932292977": 0.74, "0.9958770084729673": 0.75, "0.9966702993899259": 0.76, "0.9970389066425881": 0.77, "0.9970226719376079": 0.78, "0.9966334895278315": 0.79, "0.9958530587791484": 0.8, "0.9946296726284087": 0.81, "0.9928735891327803": 0.82, "0.9904504759116498": 0.83, "0.9871723449039742": 0.84, "0.9827853005720336": 0.85, "0.97695330085649": 0.86, "0.9692369685776062": 0.87, "0.9590662826823487": 0.88, "0.9457057140838625": 0.89, "0.9282100391473987": 0.9, "0.9053686530967862": 0.91, "0.8756357018502614": 0.92, "0.8370427377019471": 0.93, "0.7870898623684863": 0.94, "0.7226104268422548": 0.95, "0.639603283139765": 0.96, "0.5330252947455693": 0.97, "0.3965352702211031": 0.98, "0.22217864060085338": 0.99}
f = [(float(i), x) for i, x in point_probability.items() if x < .70 and x > .3]


def win_prob_to_pt_prob(p):
    if p is None:
        return .5
    return min(f, key=lambda x: abs(x[0]-p))[1]


''' Logistic regression model trained offline: Returns the win probability given a score differential
    Coded here because it is lighter weight than importing sklearn just for this at runtime'''


def model(x):
    x = 0.00847265 * x
    return 1 / (1 + exp(-x))





''' probability of a win given a score and a probability of winning each point'''


def simulate_game(p, home=0, away=0, game_to=15):
    if home >= game_to:
        return 1
    if away >= game_to:
        return 0
    wins = 0
    for i in range(100):
        home_score = home
        away_score = away
        while max(home_score,away_score)<game_to:
            if random.random()<p:
                home_score +=1
            else:
                away_score+=1
        if home_score == game_to:
            wins+=1

    return wins/100


''' Dealing with tweets'''


def tweets_from_time(team, game_time):
    if team not in handles:
        return []
    handle = handles[team]
    tweets = twitter_client.get(handle, start=int((game_time - datetime.timedelta(
        minutes=5)).timestamp()), end=int((game_time + datetime.timedelta(minutes=100)).timestamp()))
    return tweets


''' baseline tweet parsing'''


def parse_direction(tweet):
    good = ['us', 'good guys', 'win']
    bad = ['them', 'bad guys', 'lose']
    if sum([word in tweet for word in good]) > 0:
        return 1
    if sum([word in tweet for word in bad]) > 0:
        return -1
    return 0


def parse_score(tweet):
    matches = re.findall("(\d+)-(\d+)", tweet)
    if matches == []:
        return None
    (a, b) = matches[0]
    a = int(a)
    b = int(b)
    direction = parse_direction(tweet)
    if direction >= 0:
        return (max(a, b), min(a, b))
    if direction == -1:
        return (min(a, b), max(a, b))


''' dealing with games '''
GameStruct = namedtuple("GameStruct", ['home', 'away', 'score', 'score_history',
                                       'prob_history', 'away_probs', 'all_tweets', 'tournament', 'game_time'])



def parse_game(g, reverse=False):
    game_time = datetime.datetime.fromtimestamp(g['timestamp'])
    game_status = g['game_status']
    home = g['home']
    away = g['away']
    try:
        home_score = int(g['home_score'])
        away_score = int(g['away_score'])
    except:
        home_score = 0
        away_score = 0
    home_twitter = tweets_from_time(g['home'], game_time)

    away_twitter = tweets_from_time(g['away'], game_time)
    print("====", home, away)
    #print("Tweets from", home)
    all_tweets = []
    for tweet in home_twitter:
        all_tweets.append((tweet['timestamp'], (tweet['tweet']['text'], None)))
        # print(tweet)
    #print("Tweets from", away)
    for tweet in away_twitter:
        all_tweets.append((tweet['timestamp'], (None, tweet['tweet']['text'])))
        # print(tweet)
    all_tweets.sort()

    print("Total tweets", len(all_tweets))
    scores = [(0, 0)]
    for time, (home_tweet, away_tweet) in all_tweets:
        score = None
        if home_tweet:
            score = parse_score(home_tweet)
        if away_tweet:
            score = parse_score(away_tweet)
            if score:
                a, b = score
                score = (b, a)
        if score:
            a, b = score
            c, d = scores[-1]
            if a + b >= home_score + away_score and (home_score, away_score) not in scores:
                if (home_score < c) or (away_score  < d):
                    new_scores = [(x, y) for (y, x) in scores]
                    scores = new_scores
                scores.append((home_score, away_score))
                c, d = scores[-1]
                if game_status== "Final":
                    break
            if a >= c and b >= d and (a, b) not in scores:
                scores.append(score)
    c, d = scores[-1]
    if (home_score, away_score) not in scores:
        if home_score < c or away_score < d:
            new_scores = [(x,y) for (y, x) in scores]
            scores = new_scores
        scores.append((home_score, away_score))

    
    if game_status =='Final':
        game_to = max(scores[-1][0], scores[-1][1])
    else:
        game_to = 15
    print(game_status, game_status=='Final', game_to, home_score, away_score, scores[-1])
    try:
        win_prob = model(ratings.get(home, 800) - ratings.get(away, 800))
    except Exception as e:
        win_prob = .5
    score_prob = win_prob_to_pt_prob(win_prob)
    probs = []
    for a, b in scores:
        probs.append(simulate_game(score_prob, a, b, game_to=game_to))
    if reverse:
        return GameStruct(away, home, (scores[-1][1], scores[-1][0]), [(x,y) for (y,x) in scores], [1-x for x in probs], probs, all_tweets, g['tournament'], game_time.strftime("%y/%m/%d"))
    return GameStruct(home, away, (scores[-1][0], scores[-1][1]), scores, probs, [1-x for x in probs], all_tweets, g['tournament'], game_time.strftime("%y/%m/%d"))


''' get games for a team at a time range.
returns a generator (so that I can stream to a jinja template and start displaying content before I've finished)'''


def get_games(team, start, end, minimum=1):
    records = usau_client.get(team, start=start, end=end)

    for record in records:
        if team == record['home']:
            yield(parse_game(record))
        if team == record['away']:
            yield(parse_game(record, reverse=True))

app = Flask(__name__)


def stream_template(template_name, **context):
    app.update_template_context(context)
    t = app.jinja_env.get_template(template_name)
    rv = t.stream(context)
    rv.enable_buffering(5)
    return rv


@app.route("/", methods=["GET"])
def home(team=None):
    return render_template('index.html', teams=[(team, handles.get(team, ""), int(ratings.get(team, 0))) for team in ratings])


@app.route("/games/<team>", methods=["GET"])
def games(team=None):
    print(request, team)
    team = urllib.parse.unquote(team)
    start = int(request.args.get("start", 1))
    end = int(request.args.get("end", datetime.datetime.now().timestamp()))
    return Response(stream_template('games.html', games=get_games(team, start, end)))
