import type { ReactNode } from 'react';
import clsx from 'clsx';
import Link from '@docusaurus/Link';
import useDocusaurusContext from '@docusaurus/useDocusaurusContext';
import Layout from '@theme/Layout';
import HomepageFeatures from '@site/src/components/HomepageFeatures';
import Heading from '@theme/Heading';
import React, { useState, useRef, useLayoutEffect } from 'react';

import styles from './index.module.css';

function ImperfectStarSVG({ color, size }: { color: string; size: number }) {
  // Generate a star with slightly randomized points
  const points = [];
  const cx = 12, cy = 12, r1 = 10, r2 = 4.5;
  for (let i = 0; i < 10; i++) {
    const angle = (i / 10) * 2 * Math.PI - Math.PI / 2;
    const r = i % 2 === 0 ? r1 + Math.random() * 2 - 1 : r2 + Math.random() * 1.2 - 0.6;
    const x = cx + Math.cos(angle) * r;
    const y = cy + Math.sin(angle) * r;
    points.push(`${x},${y}`);
  }
  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 24 24"
      fill="none"
      style={{ display: 'block' }}
    >
      <polygon
        points={points.join(' ')}
        fill={color}
        opacity="0.92"
        filter={`drop-shadow(0 0 8px ${color}) drop-shadow(0 0 16px #fffce7)`}
      />
    </svg>
  );
}

function SparkleOverlay({ show, width, height }: { show: boolean, width: number, height: number }) {
  if (!show || !width || !height) return null;
  const N = 14; // number of sparkles
  const sparkleColors = ['#eab410', '#fffce7', '#7c3aed'];
  const sparkles = Array.from({ length: N }).map((_, i) => {
    const angle = (i / N) * 2 * Math.PI;
    // Closer to button
    const rx = width / 2 + 2;
    const ry = height / 2 + 2;
    const x = Math.cos(angle) * rx + width / 2;
    const y = Math.sin(angle) * ry + height / 2;
    // Alternate between star and glow
    const type = i % 4 === 0 ? 'star' : 'glow';
    const color = sparkleColors[i % sparkleColors.length];
    const size = type === 'star' ? Math.random() * 6 + 10 : Math.random() * 5 + 7;
    const sparkleShadow = `0 0 8px 2px ${color}, 0 0 16px 4px #fffce7`;
    return (
      <span
        key={i}
        style={{
          position: 'absolute',
          left: x - size / 2,
          top: y - size / 2,
          width: size,
          height: size,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          pointerEvents: 'none',
          animation: 'sparkle-float 1.2s infinite',
          animationDelay: `${i * 0.09}s`,
        }}
      >
        {type === 'star' ? (
          <ImperfectStarSVG color={color} size={size} />
        ) : (
          <span
            style={{
              width: size,
              height: size,
              background: `radial-gradient(circle, ${color} 70%, transparent 100%)`,
              borderRadius: '50%',
              opacity: 0.92,
              boxShadow: sparkleShadow,
              display: 'block',
            }}
          />
        )}
      </span>
    );
  });
  return (
    <span style={{
      position: 'absolute',
      left: 0,
      top: 0,
      width: width,
      height: height,
      pointerEvents: 'none',
      zIndex: 10,
      overflow: 'visible',
      display: 'block',
    }}>
      {sparkles}
      <style>{`
        @keyframes sparkle-float {
          0% { transform: scale(1) translateY(0); opacity: 0.95; }
          50% { transform: scale(1.15) translateY(-5px); opacity: 1; }
          100% { transform: scale(1) translateY(0); opacity: 0.95; }
        }
      `}</style>
    </span>
  );
}

function HomepageHeader() {
  const { siteConfig } = useDocusaurusContext();
  const [hover, setHover] = useState(false);
  const [btnSize, setBtnSize] = useState({ width: 0, height: 0 });
  const btnRef = useRef<HTMLAnchorElement>(null);

  useLayoutEffect(() => {
    if (btnRef.current) {
      const rect = btnRef.current.getBoundingClientRect();
      setBtnSize({ width: rect.width, height: rect.height });
    }
  }, [hover]);

  return (
    <header className={clsx('hero hero--primary', styles.heroBanner)}>
      <div className="container">
        <Heading as="h1" className={styles.hero__title}>
          <span className={styles.hero__magicIcon}>✨</span>
          {siteConfig.title}
          <span className={styles.hero__magicIcon}>🪄</span>
        </Heading>
        <p className={styles.hero__subtitle}>{siteConfig.tagline}</p>
        <div className={styles.buttons}>
          <div
            style={{ position: 'relative', display: 'inline-block' }}
            onMouseEnter={() => setHover(true)}
            onMouseLeave={() => setHover(false)}
          >
            <Link
              ref={btnRef}
              className="button button--secondary button--lg"
              style={{
                '--ifm-button-background-color': '#7c3aed',
                '--ifm-button-color': '#fffce7',
                '--ifm-button-border-color': '#7c3aed',
                color: '#fffce7',
                position: 'relative',
                zIndex: 3,
                overflow: 'visible',
                transition: 'box-shadow 0.4s cubic-bezier(.4,2,.6,1)',
              } as any}
              to="/docs/intro"
            >
              RAG Tutorial - 2 hours ✨
              <SparkleOverlay show={hover} width={btnSize.width} height={btnSize.height} />
            </Link>
          </div>
        </div>
      </div>
      {/* Gradient overlay for blending */}
      <div style={{
        position: 'absolute',
        left: 0,
        bottom: 0,
        width: '100%',
        height: 32,
        pointerEvents: 'none',
        background: 'linear-gradient(180deg, transparent 0%, #19181b 100%)',
        zIndex: 10
      }} />
    </header>
  );
}

export default function Home(): ReactNode {
  const { siteConfig } = useDocusaurusContext();
  return (
    <Layout
      title={`Hello from ${siteConfig.title}`}
      description="Description will go into a meta tag in <head />">
      <HomepageHeader />
      <main>
        <HomepageFeatures />
      </main>
    </Layout>
  );
}
