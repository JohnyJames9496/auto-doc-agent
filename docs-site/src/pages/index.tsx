import type {ReactNode} from 'react';
import clsx from 'clsx';
import Link from '@docusaurus/Link';
import useDocusaurusContext from '@docusaurus/useDocusaurusContext';
import Layout from '@theme/Layout';
import Heading from '@theme/Heading';
import styles from './index.module.css';

function HomepageHeader() {
  const {siteConfig} = useDocusaurusContext();
  return (
    <header className={clsx('hero hero--primary', styles.heroBanner)}>
      <div className="container">
        <Heading as="h1" className="hero__title">
          {siteConfig.title}
        </Heading>
        <p className="hero__subtitle">{siteConfig.tagline}</p>
        <div className={styles.buttons}>
          <Link
            className="button button--secondary button--lg"
            to="/intro"
            style={{marginRight: '10px'}}>
            Get Started 🚀
          </Link>
          <Link
            className="button button--secondary button--lg"
            href="https://marketplace.visualstudio.com/items?itemName=JohnyJames.auto-doc-agent">
            Install Extension ⚡
          </Link>
        </div>
      </div>
    </header>
  );
}

export default function Home(): ReactNode {
  const {siteConfig} = useDocusaurusContext();
  return (
    <Layout
      title={siteConfig.title}
      description="AI-powered automatic documentation generator for VSCode">
      <HomepageHeader />
      <main>
        <section style={{padding: '40px 0', textAlign: 'center'}}>
          <div className="container">
            <div className="row">
              <div className="col col--4">
                <h3>🤖 AI Powered</h3>
                <p>Uses Gemini AI to generate smart documentation for your functions automatically.</p>
              </div>
              <div className="col col--4">
                <h3>⚡ Real-time</h3>
                <p>Generates hover tooltips as you write code — zero effort required.</p>
              </div>
              <div className="col col--4">
                <h3>🐍 Multi-language</h3>
                <p>Supports Python, TypeScript and JavaScript out of the box.</p>
              </div>
            </div>
          </div>
        </section>
      </main>
    </Layout>
  );
}