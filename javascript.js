


// 原始选择器
数据管理
const originalSelector1 = '#bjui-hnav-navbar > li >> nth=2 >> div.items >> nth=0 >> ul.ztree.ztree_main >> nth=0';
document.querySelector('#bjui-hnav-navbar > li:nth-child(3) > div.items > ul.ztree.ztree_main')

const ulElement = document.querySelector('#bjui-hnav-navbar > li:nth-child(4) > div.items > ul.ztree.ztree_main');
if (ulElement) {
  const liCount = ulElement.querySelectorAll('li').length;
  console.log('LI 元素个数:', liCount);
} else {
  console.log('未找到目标 UL 元素');
}

下面有37个。


---------------------------------------

#系统管理
selector='#bjui-hnav-navbar > li >> nth=3 >> div.items >> nth=0 >> ul.ztree.ztree_main >> nth=0'>
#bjui-hnav-navbar > li:nth-child(2) > div.items > ul.ztree.ztree_main
document.querySelector('#bjui-hnav-navbar > li:nth-child(2) > div.items > ul.ztree.ztree_main')


//*[@id="bjui-hnav-tree02000000_1_ul"]
完整xpath : /html/body/div[1]/div/div[1]/div[2]/div[2]/div/div[2]/div/ul/li/ul
#bjui-hnav-tree01000000_1_a

const ulElement = document.querySelector('#bjui-hnav-tree01000000_1_ul');
if (ulElement) {
  const liCount = ulElement.querySelectorAll('li').length;
  console.log('LI 元素个数:', liCount);
} else {
  console.log('未找到目标 UL 元素');
}

---------------------------------------




#代理商管理
selector='#bjui-hnav-navbar > li >> nth=1 >> div.items >> nth=0 >> ul.ztree.ztree_main >> nth=0'>
#bjui-hnav-navbar > li:nth-child(1) > div.items > ul.ztree.ztree_main
document.querySelector('#bjui-hnav-navbar > li:nth-child(1) > div.items > ul.ztree.ztree_main')


const ulElement = document.querySelector('#bjui-hnav-tree02000000_1_ul');
if (ulElement) {
  const liCount = ulElement.querySelectorAll('li').length;
  console.log('LI 元素个数:', liCount);
} else {
  console.log('未找到目标 UL 元素');
}







// 转换为标准 CSS 选择器
let standardSelector1 = originalSelector1.replace(/ >> nth=(\d+)/g, function(match, index) {
    return `:nth-child(${parseInt(index) + 1})`;
});
// 替换剩余的 >> 为空格
standardSelector1 = standardSelector1.replace(/ >> /g, ' ');
console.log('找到了元素:', standardSelector1);

// 使用转换后的选择器查找元素
const element = document.querySelector(originalSelector1);

if (element) {
    console.log('找到了元素:', element);
} else {
    console.log('未找到匹配的元素。');
}

// 使用转换后的选择器查找元素
element1 = document.querySelector('#bjui-hnav-navbar > li >> nth=2 >> div.items >> nth=0 >> ul.ztree.ztree_main >> nth=0');

if (element1) {
    console.log('找到了元素:', element1);
} else {
    console.log('未找到匹配的元素。');
}
