from bs4 import BeautifulSoup

def get_inner_text(html_string):
    soup = BeautifulSoup(html_string, 'html.parser')
    target_div = soup.find('div', {
        'data-testid':'message_text_content'
    })
    if target_div:
        return target_div.get_text()
    else:
        return ""

# 示例用法
html = """
<div class="container-jODEnh chrome70-container" style="--right-side-width: 0px; --center-content-max-width: 848px;">
    <div class="inner-eE95c9 inner-item-aPP257" data-target-id="message-box-target-id" data-testid="union_message">
        <div data-testid="message-block-container" class="message-block-container-cloZOG">
            <div data-testid="receive_message" data-message-id="4938232039321602" class="message-box-ZWbBdF">
                <div class="message-box-content-wrapper-srHdUj">
                    <div class="message-content message-box-content-otxGGw receive-message-box-content-x5iBzO samantha-message-box-content-aDu1aK" data-testid="message_content">
                        <div class="think-collapse-block-iC7Hni">
                            <div class="think-collapse-button-dxR0mY" data-testid="think_collapse_button">已完成思考
                                <span role="img" class="semi-icon semi-icon-default think-collapse-button-icon-LYm92y icon-open-x8rlwo">
                                    <svg xmlns="http://www.w3.org/2000/svg" width="1em" height="1em" fill="none" viewBox="0 0 24 24"><path fill="currentColor" d="M21.707 17.293a1 1 0 0 1-1.414 0L12 9l-8.293 8.293a1 1 0 0 1-1.414-1.414l8.293-8.293a2 2 0 0 1 2.828 0l8.293 8.293a1 1 0 0 1 0 1.414"></path></svg>
                                </span>
                            </div>
                            <div class="think-quota-block-C07wzy mb-15" data-testid="think_quota_block">
                                <div class="think-quota-block-inner-sbM1db think-quota-block-inner-default-expand-fMp7pc">
                                    <div theme-mode="light" class="container-hfX5E8 flow-markdown-body theme-samantha-yJEgBp think-quota-block-mdbox-SrFy_v" dir="ltr" data-show-indicator="false">
                                        <div class="auto-hide-last-sibling-br paragraph-qzbcQC paragraph-element">好，我现在要提取这张图片中的文字。首先，我需要仔细观察图片，按照从上到下、从右到左的顺序来读取。图片的标题是 “莊子補正卷六下”，然后是 “外篇 秋水第十七”。接下来是正文：“秋水時至，百川灌河，涇流之大，兩涘渚崖之間不辯牛馬。【一注】言其廣也。” 然后是【疏】的部分：“河，孟津也。涇，通也，岸也。渚，洲也。水中之可居曰洲也。大水生于春而旺于秋，素陰杰猛，盛多霖潦，故秋水至也。既而凡百川谷，皆灌注黄河，通流盈滿，其水甚大，涯岸曠闊，洲渚迢遞，遂使隔水遠看，不辯牛之與馬也。” 再看【釋文】：“秋水李雲：水生於春，壯於秋。白虎通云：水，準也。灌河古亂反。涇音經。司馬云：涇，通也。崔本作徑，直度曰徑。又云：字或作逕。兩涘音俟。涯也。渚同馬云：水中可居曰渚。【釋名】云：渚，遮也。體高能遮水，使從旁回也。崖字又作涯，亦作厓，並同。○典案：御覽六二引作涯。一與釋文本合。疏：涯際也。是成本作涯。不辯牛馬辯别也。言廣大，故望不分别也。于是焉河伯欣然自喜，以天下之美爲盡在己。【疏】河伯，河神也。姓馮，名夷，華陰潼鄉堤首人，得水仙之道。河既大，故欣然。” 最后看页码 “四五三”。现在把这些文字整理出来，确保准确无误。</div>
                                        <br class="container-eLPxqH wrapper-wt12I4 undefined">
                                    </div>
                                </div>
                            </div>
                        </div>
                        <div data-testid="message_text_content" theme-mode="light" class="container-hfX5E8 flow-markdown-body theme-samantha-yJEgBp" dir="ltr" data-show-indicator="false"><div class="auto-hide-last-sibling-br paragraph-qzbcQC paragraph-element br-paragraph-space">莊子補正卷六下<br class="container-eLPxqH wrapper-wt12I4 undefined">外篇 秋水第十七<br class="container-eLPxqH wrapper-wt12I4 undefined">秋水時至，百川灌河，涇流之大，兩涘渚崖之間不辯牛馬。【一注】言其廣也。<br class="container-eLPxqH wrapper-wt12I4 undefined">【疏】河，孟津也。涇，通也，岸也。渚，洲也。水中之可居曰洲也。大水生于春而旺于秋，素陰杰猛，盛多霖潦，故秋水至也。既而凡百川谷，皆灌注黄河，通流盈滿，其水甚大，涯岸曠闊，洲渚迢遞，遂使隔水遠看，不辯牛之與馬也。<br class="container-eLPxqH wrapper-wt12I4 undefined">【釋文】秋水李雲：水生於春，壯於秋。白虎通云：水，準也。灌河古亂反。涇音經。司馬云：涇，通也。崔本作徑，直度曰徑。又云：字或作逕。兩涘音俟。涯也。渚同馬云：水中可居曰渚。【釋名】云：渚，遮也。體高能遮水，使從旁回也。崖字又作涯，亦作厓，並同。○典案：御覽六二引作涯。一與釋文本合。疏：涯際也。是成本作涯。不辯牛馬辯别也。言廣大，故望不分别也。于是焉河伯欣然自喜，以天下之美爲盡在己。【疏】河伯，河神也。姓馮，名夷，華陰潼鄉堤首人，得水仙之道。河既大，故欣然。<br class="container-eLPxqH wrapper-wt12I4 undefined">四五三</div><br class="container-eLPxqH wrapper-wt12I4 undefined">
                        </div><div class="flex gap-8"></div></div></div><div class="answer-action-bar-dK8PGb bottom-action-bar-wrapper-m4142O hide-N3dd2v answer-action-bar" data-testid="message_action_bar"></div></div></div></div></div>
"""

print(get_inner_text(html))