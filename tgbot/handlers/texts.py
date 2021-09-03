import os

MAIN_CHAT_ID = -int(os.getenv('MAIN_CHAT_ID'))
# MAIN_CHAT_ID = 1

SERVICES = '''
|К|а|н|а|л| |П|р|о|ф|к|о|м|а| |с|т|у|д|е|н|т|о|в|:| |@|p|r|o|f|k|o|m|m|i|p|t|
|В|а|к|а|н|с|и|и| |и| |р|е|з|ю|м|е|:| |@|p|h|y|s|t|e|c|h|c|a|r|e|e|r|c|h|a|n|n|e|l|
|Б|о|н|у|с|н|ы|е| |к|а|р|т|ы|:| |@|p|h|y|s|t|e|c|h|c|a|r|d|
|З|н|а|к|о|м|с|т|в|а|:| |@|q|u|a|l|i|d|a|t|e|_|b|o|t|
|I|n|s|t|a|g|r|a|m| |l|i|k|e|s|:| |@|l|i|k|e|m|e|u|p|b|o|t|
|П|е|р|с|о|н|а|л|ь|н|а|я| |л|е|н|т|а| |м|е|м|о|в|:| |@|f|f|m|e|m|e|s|b|o|t|
|Ф|и|з|т|е|х|и| |ш|у|т|я|т|:| |@|f|i|z|t|e|h|j|o|k|e|
|Ф|и|з|к|е|к|:| |@|p|h|y|s|k|e|k|_|o|r|i|g|i|n|a|l|
|
|К|а|н|а|л| |М|Ф|Т|И|:| |@|m|i|p|t|r|u|
|П|о|т|о|к|:| |@|m|i|p|t|s|t|r|e|a|m|
|Ф|Э|Ф|М| |М|Ф|Т|И|:| |@|s|e|p|m|p|
|С|т|у|д|с|о|в|е|т| |Ф|П|М|И|:| |@|s|t|f|p|m|i|
|Е|щ|ё| |о|д|и|н| |к|л|а|с|с|н|ы|й| |б|о|т|:| |@|u|n|i|_|h|e|l|p|_|b|o|t|
'''.replace('|', '')

CHATS = """
|P|y|t|h|o|n|:| |@|i|m|p|o|r|t|m|i|p|t|
|R|u|s|t|:| |@|r|u|s|t|a|m|i|p|t|
|K|o|t|l|i|n|:| |@|k|o|t|l|i|n|_|m|i|p|t|
|C|+|+|:| |@|c|c|m|i|p|t|
|J|a|v|a|:| |@|j|a|v|a|m|i|p|t|
|P|H|P|:| |@|p|h|p|m|i|p|t|
|Ф|р|о|н|т|е|н|д|:| |@|p|h|y|s|t|e|c|h|_|f|r|o|n|t|e|n|d|
|Б|э|к|е|н|д|:| |@|p|h|y|s|t|e|c|h|_|s|y|s|t|e|m|s|_|a|r|c|h|i|t|e|c|t|
|C|r|y|p|t|o|M|I|P|T|:| |п|и|с|а|т|ь| |@|k|a|r|f|l|y|
|
|А|н|г|л|и|й|с|к|и|й|:| |@|e|n|g|l|i|s|h|m|i|p|t|
|Н|е|м|е|ц|к|и|й|:| |@|d|e|u|t|s|c|h|m|i|p|t|
|И|с|п|а|н|с|к|и|й|:| |@|s|p|a|n|i|s|h|m|i|p|t|
|Ф|р|а|н|ц|у|з|с|к|и|й|:| |@|f|r|a|n|c|a|i|s|m|i|p|t|
|
|М|е|ж|д|у|н|а|р|о|д|н|ы|е| |с|т|а|ж|и|р|о|в|к|и|:| |@|m|i|p|t|_|i|n|t|e|r|n|s|h|i|p|s|
|П|у|т|е|ш|е|с|т|в|и|я|:| |@|p|h|y|s|t|e|c|h|t|r|a|v|e|l|
|А|в|т|о|л|ю|б|и|т|е|л|и|:| |@|m|i|p|t|a|u|t|o|
|В|е|л|о|Ф|и|з|т|е|х|:| |@|v|e|l|o|m|i|p|t|
|Я|х|т|-|к|л|у|б|:| |@|s|a|i|l|i|n|g|m|i|p|t|
|
|П|р|о|ф|к|о|м|.|О|б|с|у|ж|д|е|н|и|я|:| |@|p|r|o|f|k|o|m|d|i|s|c|u|s|s|i|o|n|s|
|Ф|и|з|т|е|х| |и| |з|а|к|о|н|:| |@|p|h|y|s|t|e|c|h|_|l|a|w|
|А|р|е|н|д|а| |ж|и|л|ь|я|:| |@|h|v|_|r|e|n|t|
|К|а|р|ь|е|р|а|:| |@|p|h|y|s|t|e|c|h|c|a|r|e|e|r|
|С|т|а|р|т|а|п|ы|:| |@|m|i|p|t|s|t|a|r|t|u|p|
|К|у|п|о|н|ы| |н|а| |п|и|ц|ц|у|:| |@|p|h|y|s|t|e|c|h|p|i|z|z|a|
|P|h|y|s|t|e|c|h|.|G|r|e|e|n|:| |@|p|h|y|s|t|e|c|h|_|g|r|e|e|n|
|
|Ч|а|т| |8| |о|б|щ|е|ж|и|т|и|я|:| |@|m|i|p|t|_|8|k|a|
|Ч|а|т| |9| |о|б|щ|е|ж|и|т|и|я|:| |@|n|o|f|l|o|o|d|_|9|k|a|
|Ч|а|т| |1|2| |о|б|щ|е|ж|и|т|и|я|:| |@|m|i|p|t|_|1|2|k|a|
|Ч|а|т| |З|ю|з|и|н|о|:| |@|Z|Z|c|h|a|t|t|e|r|
|
|Ч|а|т| |Ф|Э|Ф|М|:| |@|s|e|p|m|p|_|n|o|f|l|o|o|d|
|Ч|а|т| |А|б|и|т|у|р|и|е|н|т|ы| |Ф|Э|Ф|М|:| |@|a|b|i|t|u|_|s|e|p|m|p|
|Ч|а|т| |А|б|и|т|у|р|и|е|н|т|ы| |Л|Ф|И|:| |@|l|p|r|_|a|b|i|t|y|
|Ч|а|т| |А|б|и|т|у|р|и|е|н|т|ы| |Ф|П|М|И|:| |@|f|p|m|i|_|a|b|i|t|u|
|О|н|л|а|й|н| |м|а|г|и|с|т|р|а|т|у|р|ы| |М|Ф|Т|И|:| |@|o|n|l|i|n|e|_|m|i|p|t|
|
|Ф|л|у|д|:| |п|и|с|а|т|ь| |@|v|2|3|2|3|2|3|
|P|h|y|s|t|e|c|h|.| |N|o| |F|l|o|o|d|:| |н|а|ж|м|и|т|е| |/|s|t|a|r|t|
""".replace('|', '')

BLOGS = '''
|О|т| |@|o|k|h|l|o|p|k|o|v|:| |@|da|n|o|k|h|l|o|p|k|o|v|
|О|т| |@|r|e|a|l|k|o|s|t|i|n|:| |@|y|e|s|t|e|r|d|a|y|I|t|w|a|t|
|О|т| |@|g|i|p|e|r|k|u|b|c|h|i|k|:| |@|g|i|p|e|r|t|r|i|p|
'''.replace('|', '')

INVITE_LINK_MSG = ("""
|#|N|E|W|_|I|N|V|I|T|A|T|I|O|N|
|•| |C|h|a|n|n|e|l|:| |P|h|y|s|t|e|c|h|.|В|а|ж|н|о|е| |[|#|c|h|a|t|%d]|
|•| |U|s|e|r|:| |<|a| |h|r|e|f|=|"|t|g|:/|/|u|s|e|r|?|i|d|=|{|u|i|d|}|"|>\
|{|f|i|r|s|t|_|n|a|m|e|}| |{|l|a|s|t|_|n|a|m|e|}|<|/a|> \
|[|@|{|u|s|e|r|n|a|m|e|}|]| |[|#|i|d|{|u|i|d|}|]|
""" % MAIN_CHAT_ID).replace('|', '')

RULES = '''
💼 Чат предназначен только для лиц, связанных с МФТИ: \
обучающихся, выпускников, преподавателей и работников
🆕 Для добавление новых участников писать <a href="https://t.me/phystech_bot">@phystech_bot</a>
🕵🏻‍♂️ Используйте поиск по чату, прежде чем задавать вопрос
⚖️ Приветствуется сознательная самомодерация
👮Модераторы вправе производить любые действия, направленные на сохранение консистентности чата. \
Заинтересованные лица вправе получить объяснение действий модератора в \
<a href="|h|t|t|p|s|:|/|/|t|.|m|e|/|j|o|i|n|c|h|a|t|/|T|t|c|Z|Y|3|y|5|Q|9|F|j|N|T|k|y|"|>\
Чат модерации\
</a>
<b>Цели чата:</b>
👐🏻 Обеспечение взаимопомощи в экосистеме Физтеха
🕊 Сохранение атмосферы доверия и уважение к участникам
📢 Информирование участниками о важных событиях МФТИ в связке с каналом Физтех.Важное
<b>Не приветствуется:</b>
👥 Приватные беседы (коммуникации в чате между сугубо 2-3 участниками из 10+ сообщений за 15-минутный период. \
Такую беседу рекомендуется продолжить в ЛС)
🐷 Флуд и провокация флуда
🔇 Голосовые\видео сообщения
🖼 Флуд стикерами
💸 реклама любых сервисов, не связанных непосредственно со студентами Физтеха
<b>Запрещается:</b>
🤬 Мат
🏳️‍🌈 Обсуждение политической позиции (исключение: профильный чат @phystech_law)
🐑 Участие или добавление людей несвязанных с Физтехом
👮🏻‍♂️ Для отслеживания и критики модерации чата см. \
<a href="|h|t|t|p|s|:|/|/|t|.|m|e|/|j|o|i|n|c|h|a|t|/|T|t|c|Z|Y|3|y|5|Q|9|F|j|N|T|k|y|"|>\
Чат модерации\
</a>
📯 Для тех, кому нужен свободный от модерации чат: <a href="https://t.me/NoFlood">Физтех.Флуд</a>
'''.replace('|', '')
