class Data:
  pass

left_width = 150

templates = Data()

templates.multi_picture = "/templates/multi-picture.md",
templates.single_picture = "/templates/single-picture.md",
templates.share_link = "/templates/share-link.md",
templates.text_only = "/templates/text-only.md"

empty_line_before = 1
empty_line_after = 1

textfillpattern = r'<td\s+width="\d+"\s+align="right">.*</td>'
tf_yearpattern  = r'(?<!(\w|-|:))yyyy(?=-)'
tf_monthpattern = r'(?<=-)MM(?=-)'
tf_datepattern  = r'(?<=-)DD(?!(\w|-|:))'
tf_hourpattern  = r'(?<!(\w|-|:))hh(?=:)'
tf_minpattern   = r'(?<=:)mm(?!\w)'
tf_idpattern    = r'(?<=#)__id(?!\w)'

datafillpattern = r'<tr\s+data-timestamp="__timestamp"\s+data-id="__id">'
df_tstmppattern = r'(?<=\sdata-timestamp=")__timestamp(?="(\s|>))'
df_idpattern    = r'(?<=\sdata-id=")__id(?="(\s|>))'