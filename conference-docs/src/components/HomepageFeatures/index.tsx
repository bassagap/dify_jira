import type { ReactNode } from 'react';
import clsx from 'clsx';
import Heading from '@theme/Heading';
import styles from './styles.module.css';
import { useState } from 'react';

// Modal component for image enlargement
function ImageModal({ src, alt, onClose }: { src: string; alt: string; onClose: () => void }) {
  return (
    <div className={styles.modalOverlay} onClick={onClose}>
      <div className={styles.modalContent} onClick={e => e.stopPropagation()}>
        <img src={src} alt={alt} className={styles.modalImage} />
        <button className={styles.closeButton} onClick={onClose}>&times;</button>
      </div>
    </div>
  );
}

type FeatureItem = {
  title: string;
  img: string;
  alt: string;
  description: ReactNode;
};

const FeatureList: FeatureItem[] = [
  {
    title: 'Retrieval',
    img: require('@site/static/img/retrieval.png').default,
    alt: 'Retrieval',
    description: (
      <>
        <b>Retrieval</b> is the process of searching and fetching relevant information from your knowledge base or documents. It ensures your AI assistant can access the right context for every query.
      </>
    ),
  },
  {
    title: 'Augmented',
    img: require('@site/static/img/augmented.png').default,
    alt: 'Augmented',
    description: (
      <>
        <b>Augmented</b> means enhancing the AI's capabilities by combining retrieved knowledge with powerful language models. This step bridges your data and the model, making responses more accurate and context-aware.
      </>
    ),
  },
  {
    title: 'Generation',
    img: require('@site/static/img/generation.png').default,
    alt: 'Generation',
    description: (
      <>
        <b>Generation</b> is where the AI creates answers, explanations, or test cases using both the retrieved information and its own reasoning. This is the magic that delivers tailored, actionable insights for your testing needs.
      </>
    ),
  },
];

function FeatureCard({ title, img, alt, description, onImageClick, magicIcon }: FeatureItem & { onImageClick: () => void, magicIcon: ReactNode }) {
  return (
    <div className={styles.featureCard}>
      <div className={styles.cardImageContainer} onClick={onImageClick} tabIndex={0} role="button" aria-label={`Enlarge ${alt} image`}>
        <img src={img} alt={alt} className={styles.cardImage} />
        <span className={styles.cardMagicIcon}>{magicIcon}</span>
      </div>
      <Heading as="h3" className={styles.cardTitle}>{title}</Heading>
      <p className={styles.cardDescription}>{description}</p>
    </div>
  );
}

export default function HomepageFeatures(): ReactNode {
  const [modalImg, setModalImg] = useState<string | null>(null);
  const [modalAlt, setModalAlt] = useState<string>('');
  const magicIcons = [
    <span role="img" aria-label="broom">🧹</span>,
    <span role="img" aria-label="crystal ball">🔮</span>,
    <span role="img" aria-label="sparkles">✨</span>,
  ];

  return (
    <section className={styles.featuresGridSection}>
      <div className={styles.featuresGrid}>
        {FeatureList.map((item, idx) => (
          <FeatureCard
            key={idx}
            {...item}
            magicIcon={magicIcons[idx % magicIcons.length]}
            onImageClick={() => {
              setModalImg(item.img);
              setModalAlt(item.alt);
            }}
          />
        ))}
      </div>
      {modalImg && (
        <ImageModal src={modalImg} alt={modalAlt} onClose={() => setModalImg(null)} />
      )}
    </section>
  );
}
