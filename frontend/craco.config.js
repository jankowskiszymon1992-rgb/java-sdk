// Load configuration from environment or config file
const path = require('path');

// Environment variable overrides
const config = {
  disableHotReload: process.env.DISABLE_HOT_RELOAD === 'true',
};

module.exports = {
  webpack: {
    alias: {
      '@': path.resolve(__dirname, 'src'),
    },
    configure: (webpackConfig) => {
      
      // Remove console.logs in production using babel plugin
      if (process.env.NODE_ENV === 'production') {
        // Find babel-loader and add transform-remove-console plugin
        const babelLoader = webpackConfig.module.rules.find(
          (rule) => rule.oneOf
        );
        
        if (babelLoader && babelLoader.oneOf) {
          const babelRule = babelLoader.oneOf.find(
            (rule) => rule.loader && rule.loader.includes('babel-loader')
          );
          
          if (babelRule && babelRule.options && babelRule.options.plugins) {
            // Add plugin to remove console.log in production
            babelRule.options.plugins.push([
              'transform-remove-console',
              { exclude: ['error', 'warn'] } // Keep console.error and console.warn
            ]);
          }
        }
      }
      
      // Disable hot reload completely if environment variable is set
      if (config.disableHotReload) {
        // Remove hot reload related plugins
        webpackConfig.plugins = webpackConfig.plugins.filter(plugin => {
          return !(plugin.constructor.name === 'HotModuleReplacementPlugin');
        });
        
        // Disable watch mode
        webpackConfig.watch = false;
        webpackConfig.watchOptions = {
          ignored: /.*/, // Ignore all files
        };
      } else {
        // Add ignored patterns to reduce watched directories
        webpackConfig.watchOptions = {
          ...webpackConfig.watchOptions,
          ignored: [
            '**/node_modules/**',
            '**/.git/**',
            '**/build/**',
            '**/dist/**',
            '**/coverage/**',
            '**/public/**',
          ],
        };
      }

      // Copy service worker to build folder
      const CopyPlugin = require('copy-webpack-plugin');
      if (!webpackConfig.plugins) {
        webpackConfig.plugins = [];
      }
      webpackConfig.plugins.push(
        new CopyPlugin({
          patterns: [
            {
              from: path.resolve(__dirname, 'public/service-worker.js'),
              to: path.resolve(__dirname, 'build'),
            },
          ],
        })
      );
      
      return webpackConfig;
    },
  },
};