const withNextra = require('nextra')({
    theme: 'nextra-theme-blog',
    themeConfig: './theme.config.jsx',
})

module.exports = withNextra({
    distDir: 'out',
    images: {
        unoptimized: true,
    },
    output: 'export',
})
