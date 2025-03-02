const { defineConfig } = require('@vue/cli-service')
module.exports = defineConfig({
  transpileDependencies: true,
  publicPath:'/',//部署到https://abc.com/publicPath/
  outputDir:'dist',//输出到/dist/
  assetsDir:'static',//静态资源/dist/static/
  indexPath:'index.html',//主页/dist/index.html
  filenameHashing:false,//文件名哈希化
  runtimeCompiler:false,//允许template
  productionSourceMap:false,//要不要.js.map
  crossorigin:"anonymous",//<link>跨域
  integrity:false,//安全性
  devServer:{
    proxy:{//:"http://0.0.0.0:5009",//后端
    '/api': {
        target: 'http://0.0.0.0:5009',
        pathRewrite: { '^/api': '' }
    },}
  },
  lintOnSave:false,//语法检查
  
})
