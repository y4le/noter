import pytest
from noter_gpt.summarizer import LocalSummarizer, OpenAISummarizer

LOREM_IPSUM = """
Lorem ipsum dolor sit amet, consectetur adipiscing elit. Donec facilisis, turpis vitae pharetra pretium, massa arcu consectetur mi, placerat blandit metus enim a dolor. Quisque nulla nulla, mattis et augue sit amet, eleifend interdum tortor. Phasellus tincidunt diam vel pretium feugiat. Cras neque leo, imperdiet in eros ut, ornare varius ex. Duis blandit ante id enim fringilla, quis maximus urna varius. Phasellus finibus ac sem et sollicitudin. Integer eu lorem suscipit, tempus ex sit amet, volutpat nisi. Curabitur eleifend eu neque id vestibulum. Ut condimentum aliquet felis fringilla accumsan. Nulla et libero tempus, finibus est ac, fringilla nibh. Interdum et malesuada fames ac ante ipsum primis in faucibus. Etiam id velit non purus tempor condimentum. Nam sit amet tempor justo. Quisque a velit sed sem tristique lobortis. Duis porta tincidunt ultrices.

Vivamus venenatis dictum felis a sollicitudin. Sed vehicula libero diam, quis porta diam viverra in. Praesent aliquam odio lorem, eget vehicula magna feugiat eget. Praesent id finibus augue. Praesent at faucibus magna. Etiam sem nisi, congue vel mi sit amet, aliquet molestie leo. Ut hendrerit tellus ut felis pharetra accumsan. Pellentesque porta est nec neque blandit, nec commodo est hendrerit.

Suspendisse sed ligula tempor leo eleifend scelerisque. Etiam placerat convallis varius. Nulla facilisi. Sed sollicitudin consectetur velit id volutpat. Mauris turpis lacus, euismod vitae egestas quis, rutrum sed urna. Nunc id vulputate ipsum. In hac habitasse platea dictumst. Cras vel purus at augue aliquam fringilla. Donec vitae maximus leo. Mauris ultrices, urna eu viverra volutpat, urna dui facilisis arcu, et tincidunt lorem nisi nec ligula. Nullam volutpat, tortor at tempus aliquam, mi urna dictum neque, eget sodales augue orci ac tortor.

Curabitur ac finibus sem. Duis sed rutrum quam, eu pharetra nisi. Mauris ac nulla quam. Donec tempus ullamcorper massa eget fringilla. Phasellus et arcu pharetra, consectetur quam sit amet, fringilla quam. Duis tellus dolor, molestie quis felis quis, fringilla ullamcorper elit. Suspendisse laoreet, nulla ut faucibus molestie, tortor neque finibus mi, ut iaculis neque nisl sit amet leo.

Praesent ullamcorper porttitor arcu ac mattis. Nam vehicula interdum mollis. Suspendisse fermentum, est ut dictum ultrices, libero nibh aliquam lorem, ac vestibulum arcu nibh eu tortor. Etiam ornare metus blandit sollicitudin maximus. Fusce iaculis leo feugiat nunc varius, at tempor augue efficitur. Nam commodo molestie odio at lacinia. Orci varius natoque penatibus et magnis dis parturient montes, nascetur ridiculus mus. Vivamus a feugiat purus. Aenean facilisis pulvinar ex a vehicula. Praesent ornare est metus, eu iaculis quam ullamcorper eget. Suspendisse eleifend, diam nec ornare congue, elit lacus blandit ligula, id rhoncus massa dui nec lacus. Nunc egestas, magna id commodo volutpat, orci tortor convallis ex, sit amet iaculis leo dui vitae dolor. Mauris ultrices in libero vel rutrum. Fusce fringilla magna id sapien sollicitudin porta.

Quisque sed elementum leo. Morbi augue odio, tempus aliquet bibendum sit amet, dignissim vel nisi. Proin sed eros id nunc lacinia gravida. Fusce consectetur accumsan mi, quis consequat neque suscipit eget. Nam tristique, elit at efficitur lacinia, lacus elit feugiat leo, posuere maximus sapien libero id lacus. Class aptent taciti sociosqu ad litora torquent per conubia nostra, per inceptos himenaeos. Morbi aliquet sapien non eros fringilla, sed tincidunt dolor tempor. Sed aliquet ultrices sapien ac mollis. Donec suscipit urna felis, interdum laoreet mauris scelerisque quis. Cras luctus erat et neque lacinia tempor. Aliquam pharetra ex eu quam volutpat, at vulputate eros dapibus. Morbi ornare vitae est ac tristique. Praesent convallis nisi dictum lorem condimentum, a sollicitudin elit dictum.

Nullam lacinia luctus est ut fermentum. Mauris molestie auctor quam ut sodales. Fusce suscipit nisi at sapien dapibus congue. Pellentesque habitant morbi tristique senectus et netus et malesuada fames ac turpis egestas. Quisque venenatis rutrum lectus, eu sagittis sapien imperdiet id. Pellentesque ac tortor ut eros facilisis semper quis et arcu. Ut tincidunt leo lacus, ac mollis eros aliquet in. Sed bibendum lacus eu volutpat gravida. Etiam vitae lectus consectetur, tempor ipsum sed, aliquet augue. Morbi placerat, erat eu facilisis condimentum, felis eros ullamcorper felis, eget convallis arcu purus sed lorem. Nullam velit ante, dictum vitae tempus in, dictum at velit. Morbi blandit nunc a nibh commodo tempus. Praesent imperdiet nulla sit amet mollis bibendum. Morbi luctus turpis id aliquet mollis.

Vivamus vitae tellus quis massa ornare malesuada. Nullam volutpat auctor pulvinar. Integer semper tincidunt arcu in convallis. Suspendisse commodo ligula ac lectus viverra, vitae molestie nunc viverra. Donec sed ante a massa finibus auctor ac sit amet dolor. Morbi dui dui, pharetra in luctus sit amet, ullamcorper nec nulla. Morbi id fringilla metus. Cras id enim nec augue scelerisque vulputate fermentum id est. Ut condimentum congue suscipit.

Vestibulum hendrerit nulla nec tincidunt eleifend. Integer molestie posuere vestibulum. Sed vulputate nunc quis convallis scelerisque. Fusce porta velit urna, eget efficitur nibh consectetur facilisis. Proin bibendum, metus a faucibus vulputate, nibh mi porta leo, et luctus magna est vel est. Morbi ac congue neque. Etiam tincidunt lacinia congue. Quisque sit amet nisl lobortis nunc mollis fermentum. Donec aliquet imperdiet tincidunt. Integer bibendum metus leo, vitae lacinia enim lobortis nec. Phasellus a nunc at ex blandit facilisis non quis purus. Morbi venenatis diam vitae urna finibus sodales. Morbi interdum ornare ultricies.

Donec sed elementum dui. Sed eleifend pulvinar nisl, id cursus lectus tempor sit amet. Pellentesque cursus velit eget sem vehicula euismod. Vestibulum ac auctor quam, non faucibus diam. Mauris pulvinar mi a pharetra tincidunt. Nulla facilisi. Pellentesque posuere ipsum sit amet nisl rutrum placerat. Pellentesque fringilla neque vitae vestibulum faucibus. Vestibulum ornare augue quam, vitae dapibus nisi egestas nec. Nullam imperdiet non neque eu aliquet. Phasellus ac consequat nunc, maximus hendrerit urna. Maecenas vitae sapien faucibus, interdum turpis id, convallis massa. 
"""

def test_local_summarizer():
    summarizer = LocalSummarizer()
    summary = summarizer.summarize_text(LOREM_IPSUM)
    assert isinstance(summary, str)
    assert len(summary) < len(LOREM_IPSUM)

def test_openai_summarizer():
    summarizer = OpenAISummarizer()
    summary = summarizer.summarize_text(LOREM_IPSUM)
    assert isinstance(summary, str)
    assert len(summary) < len(LOREM_IPSUM)

def test_local_summarizer_cache():
    summarizer = LocalSummarizer()
    text = "This is a test text for summarization."
    summary1 = summarizer.summarize_text(text)
    summary2 = summarizer.summarize_text(text)
    assert summary1 == summary2

def test_openai_summarizer_cache():
    summarizer = OpenAISummarizer()
    text = "This is a test text for summarization."
    summary1 = summarizer.summarize_text(text)
    summary2 = summarizer.summarize_text(text)
    assert summary1 == summary2
