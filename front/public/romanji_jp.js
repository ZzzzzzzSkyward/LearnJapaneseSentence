class TrieNode {
    constructor () {
        this.children = new Map();
        this.value = null;
    }
}

class CharTrie {
    constructor () {
        this.root = new TrieNode();
    }

    insert ( key, value ) {
        let node = this.root;
        for ( const char of key ) {
            if ( !node.children.has( char ) ) {
                node.children.set( char, new TrieNode() );
            }
            node = node.children.get( char );
        }
        node.value = value;
    }

    prefixes ( input ) {
        let node = this.root;
        let currentKey = '';
        const results = [];
        for ( const char of input ) {
            currentKey += char;
            if ( !node.children.has( char ) ) break;
            node = node.children.get( char );
            if ( node.value !== null ) results.push( { key: currentKey, value: node.value } );
        }
        return results;
    }
}
const romanjiTrie = new CharTrie();
let loadJson = function () {
    let fn = function ( data ) {
        Object.entries( JSON.parse( data ) ).forEach( ( [ key, value ] ) => {
            romanjiTrie.insert( key, value );
        } );
    }
    let flag = false;
    try {
        const { readFile } = require( "fs" );
        readFile( "romaji_jp.jsond", "utf8", ( err, data ) => {
            if ( data )
                fn( data );
        } );
        flag = true;
    } catch ( e ) {
    }
    if ( !flag ) {
        fetch( "romaji_jp.jsond" ).then( res => res.text() ).then( fn );
    }
}


function romajiToJapanese ( romaji ) {
    const words = [];
    while ( romaji.length > 0 ) {
        const prefixes = romanjiTrie.prefixes( romaji );
        if ( prefixes.length > 0 ) {
            const longest = prefixes[ prefixes.length - 1 ];
            words.push( longest.value );
            romaji = romaji.slice( longest.key.length );
        } else {
            words.push( romaji[ 0 ] );
            romaji = romaji.slice( 1 );
        }
    }
    return words.join( '' );
}
loadJson();
function IsJapaneseOnly ( text ) {
    for ( let i = 0; i < text.length; i++ ) {
        let c = text.charCodeAt( i );
        if ( 0x3041 <= c && c <= 0x309F ) {

        }
        else if ( 0x30a1 <= c && c <= 0x30f7 ) { } else {
            return false;
        }
    }
    return true;
}