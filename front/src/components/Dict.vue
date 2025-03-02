<template>
    <div id="dict-container">
        <h1>日语</h1>
        <div class="dict-input">
            <el-autocomplete v-model="dict_input" ref="dict_input_ref" :fetch-suggestions="querySearch" :debounce="500"
                :highlight-first-item="true" trigger-on-focus="true" clearable class="inline-input w-50"
                :placeholder="dict_placeholder" @select="OnSelectDictItem" @keyup.enter="OnDictInputKeyUpTrySearch"
                @keyup.control="OnDictInputKeyUpShowMenu" @keyup.up="OnDictInputUpHistory"
                @keyup.down="OnDictInputDownHistory">
                <template #prefix>
                    <div class="dict-func" @click="OnDictInputClickShowMenu">
                        <span class="disable-select">
                            {{ dict_input_func }}
                        </span>
                    </div>
                </template>
                <template #default="{ item }">
                    <div class="dict-input-item">
                        <p>
                            <span v-if="item.func" class="dict-item-func">{{ item.func }}</span>
                            {{ item.value }}
                        </p>
                    </div>
                </template>
            </el-autocomplete>
            <el-switch class="dict-input-web-switch" v-model="is_web_search" active-text="在线" inactive-text="离线"
                inline-prompt @click="ToggleWebSearch">搜索</el-switch>
            <el-select v-model="dict_history" filterable placeholder="历史" class="dict-history"
                @change="OnSelectHistoryItem">
                <el-option v-for="item in dict_history_items" :key="item.api + item.text + item.uid || '0'"
                    :label="item.api + '|' + item.text" :value="item" />
            </el-select>
        </div>
        <div id="meaning-container">
            <div id="tokenResults"></div>
            <div id="meaning-content"></div>
        </div>
    </div>
</template>
<script setup>
import { ElMessage } from 'element-plus'
import { ref, onMounted } from 'vue';
import { marked } from 'marked';
const dict_input = ref( '' );
const is_web_search = ref( false );
const dict_history = ref( null );
const dict_history_items = ref( [] );
const meaning = ref( '' );
const dict_input_ref = ref();
const dict_placeholder = ref( '输入罗马音、汉字，按ctrl触发菜单' );
const dict_input_func = ref( '查词' );
onMounted( () => OnMount() );
const funcs = {
    "查词": {
        default: true,
        endpoint: "lookup",
        cb: ( r ) => process_lookup( r )
    },
    "翻译": {
        endpoint: "translate",
        cb: ( r ) => process_translate( r )
    },
    "解释": {
        endpoint: "explain",
        cb: ( r ) => process_explain( r )
    },
    "联想": {
        endpoint: "memorize",
        cb: ( r ) => process_memorize( r )
    }
}
const querySearch = ( queryString, cb ) => {
    let results = [];
    if ( queryString === true ) {
        //高级功能
        queryString = dict_input.value;
        for ( let i in funcs ) {
            if ( i != dict_input_func.value ) {
                results.push( { value: `${ queryString }`, func: i } )
            }
        }
        return results;
    }
    let tokens = queryString.split( ' ' ).filter( x => x );
    if ( tokens.length ) {
        let former_tokens = tokens.slice( 0, tokens.length - 1 ).join( '' );
        let last_token = tokens[ tokens.length - 1 ];
        let last_token_jp = LocalLookupPinyin( last_token );
        let last_token_jp_upper = LocalLookupPinyin( last_token.toUpperCase() );
        let concat_tokens_upper = former_tokens + last_token_jp_upper;
        let concat_tokens = former_tokens + last_token_jp;
        let result_set = new Set();
        let english_token = LookupEnglishWord( last_token );
        let concat_tokens_english = former_tokens + english_token;
        result_set.add( queryString );
        result_set.add( concat_tokens );
        result_set.add( concat_tokens_upper );
        result_set.add( concat_tokens_english );
        for ( let i of result_set ) {
            if ( i != "" ) {
                results.push( { value: i } )
            }
        }
    }
    cb( results );
};
const OnDictInputKeyUpShowMenu = () => {
    dict_input_ref.value.getData( true );
}
const OnDictInputClickShowMenu = () => {
    dict_input_ref.value.focus();
    dict_input_ref.value.getData( true );
}
const OnDictInputKeyUpTrySearch = () => {
    if ( ShouldBlockKeyEvent() ) return;
    if ( dict_input.value == "" ) return;
    handleEnter();
    return OnLookupPinyin();
}
const OnSelectDictItem = ( item ) => {
    if ( item.func ) {
        dict_input_func.value = item.func;
    }
};
const ConvertMarkdown = ( text ) => {
    return marked.parse( text );
}
let katakana_regex = /^[A-Za-z0-9\u30a0-\u30ff]+$/
function is_kata ( str ) {
    return katakana_regex.test( str );
}
let ignores = [ "、", "。", "..." ];
// 处理服务器响应的函数
function process_reply ( json ) {
    // 清空现有的分词结果
    getElement( '#tokenResults' ).innerHTML = '';
    if ( !json.success ) {
        let fail = createElement( 'div' );
        fail.innerText = "解析失败";
        getElement( '#tokenResults' ).appendChild( fail );
        return;
    }
    if ( json.translation ) {
        let translation = createElement( "div", "translation" );
        translation.innerHTML = json.translation;
        getElement( '#tokenResults' ).appendChild( translation );
    }
    json.data.forEach( AppendJsonSent );
}
function createElement ( tag, classList, styles ) {
    let obj = document.createElement( tag );
    if ( classList ) {
        obj.className = classList;
    }
    if ( styles ) {
        for ( let k in styles ) {
            obj.style[ k ] = styles[ k ];
        }
    }
    return obj;
}
function getElement ( q ) {
    return document.querySelector( q );
}
function AppendJsonSent ( json ) {
    let sent = createElement( 'div', 'sent' );
    getElement( '#tokenResults' ).appendChild( sent );
    // 遍历tokens数组，创建分词结果的显示元素
    let tokens = json.tokens.map( CreateJsonToken );
    for ( let t of tokens ) {
        sent.appendChild( t );
    }
    if ( json.translation ) {
        let translation = createElement( "div", "translation" );
        translation.innerHTML = json.translation;
        sent.appendChild( translation );
    }
}
function LookupEnglishWord ( query ) {
    if ( jp_en_dict[ query ] ) {
        return jp_en_dict[ query ];
    }
    return query;
}
function CreateJsonToken ( token, index, sent ) {
    let tokenDiv = createElement( 'div' );
    tokenDiv.className = 'token';

    let word = createElement( 'div' );
    let switch_flag = false;
    if ( token.lemma_ == token.orth_ && is_kata( token.orth_ ) && jp_en_dict[ token.orth_ ] ) {
        token.lemma_ = jp_en_dict[ token.orth_ ];
        switch_flag = true;
    }
    word.className = 'jpword';
    let spoken = createElement( "span", "spoken" );
    let lemma = createElement( "span", "lemma" );
    spoken.innerHTML = token.orth_;
    lemma.innerHTML = token.lemma_;
    if ( switch_flag ) {
        spoken.innerHTML = token.lemma_;
        lemma.innerHTML = token.orth_;
    }
    if ( token.lemma_ === token.orth_ ) {
        lemma.classList.add( "hidden" );
        lemma.innerHTML = '';
    }
    word.appendChild( spoken );
    word.appendChild( lemma );
    //word.setAttribute( "contenteditable", "true" );
    let blank = false;
    if ( token.tag_ === "空白" || IsBlank( token.orth_ ) ) {
        tokenDiv.classList.add( "blank" );
        blank = true;
    }

    let romaji = createElement( 'div' );
    romaji.className = 'romaji disable-select';
    if ( !IsJapaneseOnly( token.lemma_ ) && !switch_flag ) {
        romaji.innerText = token.romaji;
    }
    else {
        romaji.classList.add( "hidden" );
    }

    let Tag = createElement( 'div' );
    Tag.className = 'pos-tag disable-select';
    Tag.innerText = token.tag_;

    // 将词语、罗马音和词性添加到分词结果容器中
    if ( ignores.includes( token.orth_ ) ) {
        romaji.innerText = " ";
        Tag.innerText = " ";
        word.classList.add( "ignore" );
    }
    tokenDiv.appendChild( romaji );
    tokenDiv.appendChild( word );
    tokenDiv.appendChild( Tag );

    //确定显示宽度
    let maxwidth = 0;
    if ( blank ) {
        maxwidth = 1;
    } else {
        maxwidth = Math.max( Tag.innerText.length, romaji.innerText.length, word
            .innerText.length, 0 );
    }
    tokenDiv.style.minWidth = Math.ceil( maxwidth / 2 ).toString() + "em";

    return tokenDiv;
}
function ListenWheel ( tokenDiv ) {
    if ( tokenDiv.cd_wheel ) return;
    AlternateLemma( tokenDiv );
    tokenDiv.cd_wheel = setTimeout( function () {
        tokenDiv.cd_wheel = null;
    }, 500 );
}
function ListenContext ( tokenDiv, e ) {
    SelectToken( tokenDiv );
    e.preventDefault();
    e.stopPropagation();
    return true;
}
function ListenSearch ( tokenDiv ) {
    OnlineSearch( tokenDiv );
}
function AlternateLemma ( tokenDiv ) {
    let orth_ = tokenDiv.getElementsByClassName( "jpword" )[ 0 ].firstElementChild.innerText;
    let lemma_ = tokenDiv.getElementsByClassName( "lemma" )[ 0 ].innerText;
    if ( lemma_ === "" ) return;
    tokenDiv.getElementsByClassName( "jpword" )[ 0 ].firstElementChild.innerText = lemma_;
    tokenDiv.getElementsByClassName( "lemma" )[ 0 ].innerText = orth_;
}

function SelectToken ( tokenDiv ) {
    tokenDiv.selected = !tokenDiv.selected;
    if ( tokenDiv.selected ) {
        tokenDiv.classList.add( "selected" );
    }
    else {
        tokenDiv.classList.remove( "selected" );
    }
}
function GetSelectedTokens () {
    let ctn = document.getElementsByClassName( "selected" );
    let tokens = [];
    for ( let i = 0; i < ctn.length; i++ ) {
        tokens.push( ctn[ i ].getElementsByClassName( "jpword" )[ 0 ].innerText );
    }
    return tokens.join( "" );
}
function IsBlank ( word ) {
    for ( let i = 0; i < word.length; i++ ) {
        let c = word.charAt( i );
        if ( c !== " " ) {
            return false;
        }
    }
    return true;
}
function OnlineSearch ( tokenDiv ) {
    let word = tokenDiv.getElementsByClassName( 'jpword' )[ 0 ].firstElementChild;
    let text = word.innerText;
    text = encodeURIComponent( text );
    let url = `https://www.weblio.jp/content_find/contains/0/${ text }`;
    OpenNewWindow( url );
}
function DisplayMeaning ( tokenDiv ) {
    let lemma = tokenDiv.querySelector( '.jpword .lemma' ).innerText;
    let spoken = tokenDiv.querySelector( '.jpword .spoken' ).innerText;
    let text = lemma || spoken;
    SendLookupRequest( text, true );
}


function Purify ( text ) {
    //trim
    text = text.trim();
    return text;
}
let oldtext = {};
let sending = false;
let request_cache = {};
function SetRequestCache ( api, text, uid, data, cb ) {
    let hashed = text + api + ( uid || "0" );
    request_cache[ hashed ] = data;
}
function GetRequestCache ( api, text, uid ) {
    let hashed = text + api + ( uid || "0" );
    return request_cache[ hashed ];
}
function SendGetRequest ( text, force, api, cb, data_str ) {
    if ( sending ) {
        ElMessage.error( "正在处理中，请稍后重试" )
        return;
    }
    sending = true;
    if ( !api ) api = "process";
    if ( typeof api !== "string" ) {
        console.error( "api must be string", api );
        return;
    }
    if ( !cb ) cb = process_reply;
    if ( typeof cb !== "function" ) {
        console.error( "cb must be function", cb );
        return;
    }
    text = Purify( text );
    if ( oldtext[ api ] == text && !force ) {
        //return;
    }
    if ( !text ) return;
    oldtext[ api ] = text;
    if ( dict_history_items.value.every( x => x.text !== text ) ) {
        dict_history_items.value.push( { api, text, cb } );
    }
    // 发送GET请求
    let xhr = new XMLHttpRequest();
    let u = `/api/${ api }?query=${ encodeURIComponent( text ) }&web=${ is_web_search.value ? "true" : "false" }`;
    if ( data_str ) {
        u += "&";
        if ( typeof data_str === "string" )
            u += data_str;
        else if ( data_str instanceof Array ) {
            u += data_str.join( "&" );
        }
    }
    xhr.open( 'GET', u, true );
    xhr.onreadystatechange = function () {
        if ( xhr.readyState === 4 ) {
            if ( xhr.status === 200 ) {
                let response = JSON.parse( xhr.responseText );
                cb( response );
                SetRequestCache( api, text, null, response, cb );
            }
            else {
                ElMessage.error( "请求失败" );
            }
            sending = false;
        }
    };
    xhr.send();
}
let lookup_cache = {};
for ( let funcname in funcs ) {
    lookup_cache[ funcname ] = {};
}
function process_lookup ( response ) {
    if ( !response.success ) {
        console.log( "lookup request failed", response );
        return;
    }
    let data = response.data;
    let ctn = getElement( "#meaning-content" );
    ctn.innerHTML = "";
    if ( data ) {
        ctn.innerHTML = data.content;
        postprocess_lookup( ctn );
        lookup_cache[ data.text ] = response;
    }
}
function process_translate ( response ) {
    let ctn = getElement( "#meaning-content" );
    ctn.innerHTML = "";
    if ( response.result ) {
        ctn.innerHTML = response.result;
    }
    else {
        ctn.innerHTML = "翻译失败";
    }
}
function process_explain ( response ) {
    let ctn = getElement( "#meaning-content" );
    ctn.innerHTML = "";
    if ( response.result ) {
        ctn.innerHTML = ConvertMarkdown( response.result );
    }
    else {
        ctn.innerHTML = "解释失败";
    }
}
function process_memorize ( response ) {
    let ctn = getElement( "#meaning-content" );
    ctn.innerHTML = "";
    if ( response.result ) {
        ctn.innerHTML = ConvertMarkdown( response.result );
    }
    else {
        ctn.innerHTML = "联想失败";
    }
}
function postprocess_lookup ( ctn ) {
    //阻止超链接跳转
    let a = ctn.getElementsByTagName( "a" );
    for ( let i = 0; i < a.length; i++ ) {
        let aa = a[ i ];
        if ( aa.href.indexOf( "search/" ) >= 0 ) {
            //jisho search
            aa.addEventListener( 'click', function ( event ) {
                // 阻止超链接的默认行为
                event.preventDefault();
                let h = aa.href;
                SendLookupRequest( h.substring( h.indexOf( "search/" ) + 7 ) )
                return true
            } );
        }
        else if ( aa.href.indexOf( "content/" ) >= 0 ) {
            //weblio search
            aa.addEventListener( 'click', function ( event ) {
                // 阻止超链接的默认行为
                event.preventDefault();
                let h = aa.href;
                SendLookupRequest( h.substring( h.indexOf( "content/" ) + 8 ) )
                return true
            } );
        }
    }
}
function SendLookupRequest ( text, force ) {
    if ( !text ) return;
    let funcname = '查词';
    //恢复被编码的text
    if ( text.indexOf( "%" ) === 0 ) text = decodeURIComponent( text );
    if ( lookup_cache[ funcname ] && lookup_cache[ funcname ][ text ] && !force ) return process_lookup( lookup_cache[ funcname ][ text ] );
    SendGetRequest( text, force, "lookup", process_lookup );
}
function SendRequestToServer ( text, funcname, force ) {
    if ( !text ) return;
    //恢复被编码的text
    if ( text.indexOf( "%" ) === 0 ) text = decodeURIComponent( text );
    if ( lookup_cache[ funcname ] && lookup_cache[ funcname ][ text ] && !force ) return funcs[ funcname ].cb( lookup_cache[ funcname ][ text ] );
    SendGetRequest( text, force, funcs[ funcname ].endpoint, funcs[ funcname ].cb );
}
function LocalLookupPinyin ( text ) {
    let ret = romajiToJapanese( text );
    return ret;
}
function GetFirstSimpleToken () {
    let area = getElement( "#pasteArea" );
    let tokens = area.value.split( /[\n ?？！!、。,.　:：「|」]/ );
    for ( let i of tokens ) {
        if ( i ) return i;
    }
}
function searchWord () {
    let selectedText = GetSelectedTokens() || GetFirstSimpleToken();
    if ( !selectedText ) return;
    if ( selectedText.length > 64 ) {
        console.log( "search word too long", selectedText );
        return
    }
    // 编码选中的文本，以确保URL的合法性
    let encodedText = encodeURIComponent( selectedText );

    // 构造Weblio字典的URL
    let dict = "https://www.weblio.jp/content/";
    let url = `${ dict }${ encodedText }`;
    return OpenNewWindow( url );
}
function OpenNewWindow ( url ) {
    // 打开新的浏览器标签页或窗口
    window.open( url, '_blank' );
}
let delay_task = null;
function SendDocRequest ( force, data ) {
    SendGetRequest( getElement( '#pasteArea' ).value, force, "process", process_reply, data );
}

function handleChange ( event, force ) {
    if ( delay_task ) {
        clearTimeout( delay_task );
    }
    delay_task = setTimeout( function () {
        let options = getOptionsStatus();
        let data = [];
        for ( let i in options ) {
            if ( options.hasOwnProperty( i ) && options[ i ] ) {
                data.push( `${ encodeURIComponent( i ) }=${ encodeURIComponent( options[ i ] ) }` );
            }
        }
        SendDocRequest( force, data );
        delay_task = null;
    }, 1000 );
}
let jp_en_dict = {};
// 页面加载完成后，给文本框添加事件监听器
function OnMount () {
    fetch( "/api/jp_en_dict" ).then( response => response.json() ).then( data => {
        if ( !data ) return;
        for ( let i in data ) jp_en_dict[ i ] = data[ i ];
    } ).catch( error => {
        console.error( 'Error fetching data:', error );
        ElMessage.error( 'Error fetching data' );
    } );
}
// 定义一个函数来获取选项的状态
function getOptionsStatus () {
    // 创建一个对象来存储状态
    let status = {
        trans: getElement( '#translate-switch' ).checked,
        lookup: getElement( '#lookup-switch' ).checked,
        engines: []
    };

    // 获取所有翻译引擎的复选框，并检查哪些被选中
    const engineCheckboxes = document.querySelectorAll( 'input[name="engine"]' );
    engineCheckboxes.forEach( checkbox => {
        if ( checkbox.checked ) {
            status.engines.push( checkbox.value );
        }
    } );

    // 返回包含所有选项状态的对象
    return status;
}
function OnSelectHistoryItem () {
    let v = dict_history.value;
    if ( !v ) return;
    let resp = GetRequestCache( v.api, v.text, v.uid );
    console.log( 'resp', resp );
    if ( resp ) {
        v.cb( resp, true );
    }
}

const history = ref( [] );
const currentHistoryIndex = ref( -1 );
const tempCurrentInput = ref( '' );
const ShouldBlockKeyEvent = () => {
    let hidden = document.querySelector( '.el-autocomplete__popper' ).getAttribute( "aria-hidden" );
    let single = dict_input_ref.value.suggestions.length == 1;
    if ( hidden !== "true" && !single ) return true;
    return false;
}
const OnDictInputUpHistory = () => {
    if ( ShouldBlockKeyEvent() ) return;
    if ( history.value.length === 0 ) return;

    if ( currentHistoryIndex.value === -1 ) {
        // 首次按上键，保存当前输入
        tempCurrentInput.value = dict_input.value;
    }

    if ( currentHistoryIndex.value < history.value.length - 1 ) {
        currentHistoryIndex.value++;
        dict_input.value = history.value[ currentHistoryIndex.value ];
    }
};

const OnDictInputDownHistory = () => {
    if ( ShouldBlockKeyEvent() ) return;
    if ( currentHistoryIndex.value === -1 ) return;

    currentHistoryIndex.value--;

    if ( currentHistoryIndex.value === -1 ) {
        dict_input.value = tempCurrentInput.value;
    } else {
        dict_input.value = history.value[ currentHistoryIndex.value ];
    }
};

const handleEnter = () => {
    // 避免重复添加相同的连续记录
    if ( history.value[ 0 ] !== dict_input.value ) {
        history.value.unshift( dict_input.value );
    }

    // 重置状态
    currentHistoryIndex.value = -1;
    tempCurrentInput.value = '';
};
function OnLookupPinyin () {
    let v = dict_input.value;
    let f = dict_input_func.value;
    console.log( v, f );
    SendRequestToServer( v, f );
}
let toggle = false;
function ToggleWebSearch () { }
function ToggleDisplayMeaning () {
    let m = getElement( "#meaning" );
    toggle = !toggle;
    if ( toggle ) {
        m.classList.add( "fixed" );
    } else {
        m.classList.remove( "fixed" );
    }

}
</script>
<script>
export default {
    name: 'Dict',
    props: {
    }
}
</script>
<style>
#dict-container {
    font-size: 2vw;
}

#dict-container .el-switch__core {
    border-radius: 0.1em;
}

.dict-input-item p {
    line-height: 1.5em;
    padding: 0;
    margin: 0.1em;
    margin-block-start: 0;
    margin-block-end: 0;
}

.dict-func {
    color: rgb(143, 9, 9);
    cursor: alias;
}

.dict-input {
    position: sticky !important;
    top: 0;
    z-index: 100;
    display: flex;
    justify-content: space-between;
    background-color: rgba(255, 255, 255, 0.082);
    opacity: 0.5;
    transform: all 0.1s ease-in-out 0s;
}
.dict-input:hover{
    background-color: rgba(255, 255, 255, 0.799);
    opacity: 1;
}
.dict-input .el-input__wrapper{
    --el-input-bg-color:rgba(255, 255, 255, 0.199);
}
.dict-input .el-select{
    --el-fill-color-blank:rgba(255, 255, 255, 0.199);
}

.dict-input .inline-input {
    flex: 4;
}

.dict-input .dict-history {
    flex: 1;
}

.dict-input .dict-input-web-switch {
    --el-switch-off-color: rgb(255, 209, 58);
    margin-left: 0.1em;
    margin-right: 0.1em;
    --el-border-radius-circle: 4%;
}
</style>