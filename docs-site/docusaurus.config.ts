import {themes as prismThemes} from 'prism-react-renderer';
import type {Config} from '@docusaurus/types';
import type * as Preset from '@docusaurus/preset-classic';

const config: Config = {
  title: 'Auto-Doc Agent',
  tagline: 'Always up-to-date documentation, generated automatically',
  favicon: 'img/favicon.ico',
  url: 'https://your-project.vercel.app',
  baseUrl: '/',
  organizationName: 'JohnyJames9496',
  projectName: 'auto-doc-agent',
  onBrokenLinks: 'warn',
  onBrokenMarkdownLinks: 'warn',

  i18n: {
    defaultLocale: 'en',
    locales: ['en'],
  },

  presets: [
    [
      'classic',
      {
        docs: {
          sidebarPath: './sidebars.ts',
          routeBasePath: '/',
        },
        blog: false,
        theme: {
          customCss: './src/css/custom.css',
        },
      } satisfies Preset.Options,
    ],
  ],

  themeConfig: {
    navbar: {
      title: 'Auto-Doc Agent',
      items: [
        {
          href: 'https://github.com/JohnyJames9496/auto-doc-agent',
          label: 'GitHub',
          position: 'right',
        },
      ],
    },
    footer: {
      style: 'dark',
      copyright: `Built with Auto-Doc Agent — AI-powered documentation`,
    },
    colorMode: {
      defaultMode: 'dark',
    },
    prism: {
      theme: prismThemes.github,
      darkTheme: prismThemes.dracula,
    },
  } satisfies Preset.ThemeConfig,
};

export default config;