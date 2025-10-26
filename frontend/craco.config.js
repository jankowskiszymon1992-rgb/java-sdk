// Load configuration from environment or config file
const path = require('path');

// Environment variable overrides
const config = {
  disableHotReload: process.env.DISABLE_HOT_RELOAD === 'true',
};

module.exports = {
  devServer: {
    client: {
      overlay: {
        errors: true,
        warnings: false,
        runtimeErrors: (error) => {
          // Ignore ResizeObserver errors - they are harmless
          if (error.message && error.message.includes('ResizeObserver')) {
            return false;
          }
          return true;
        },
      },
    },
  },
  webpack: {
    alias: {
      '@': path.resolve(__dirname, 'src'),
    },
    configure: (webpackConfig) => {
      
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

      // Suppress DevTools auto-open by removing console logs in production
      if (process.env.NODE_ENV === 'production') {
        // Configure Terser to remove console.logs
        const TerserPlugin = require('terser-webpack-plugin');
        webpackConfig.optimization.minimizer = [
          new TerserPlugin({
            terserOptions: {
              compress: {
                drop_console: true, // Remove all console statements
              },
            },
          }),
        ];
      }
      
      return webpackConfig;
    },
  },
};