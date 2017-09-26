var webpack = require('webpack'),
    path = require('path');

module.exports = {
   entry:  './web_client/app.js',
   output:  {
       path: `${__dirname}/webpack_static/js`,
       filename: 'app.js'
   },
   resolve: {
       extensions: ['.js', '.jsx'],
   },
   module: {
       rules: [
          // the 'transform-runtime' plugin tells babel to require the runtime
          // instead of inlining it.
          {
            test: /\.jsx?$/,
            exclude: /(node_modules|bower_components)/,
            use: {
              loader: 'babel-loader',
              options: {
                presets: ['env', 'es2015', 'react'],
                plugins: ['transform-runtime']
              },
            }
          },
          {
            test: /\.css$/,
            exclude: /(node_modules|bower_components)/,
            loader: "style-loader!css-loader"
          }
        ]
   }
}
