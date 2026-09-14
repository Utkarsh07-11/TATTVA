import React, { useEffect, useRef, useState } from 'react';

export default function BlockRevealImage({
  src,
  alt = '',
  className = '',
  imageClassName = 'w-full h-full object-cover',
  aspectRatio = 'aspect-[16/10]',
  blockColor = 'bg-[#d4a574]', // Copper / Amber or Slate
  caption = null,
  captionPosition = 'bottom',
  delay = 100,
}) {
  const containerRef = useRef(null);
  const [isVisible, setIsVisible] = useState(false);
  const [animationKey, setAnimationKey] = useState(0);

  useEffect(() => {
    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          setIsVisible(true);
        }
      },
      { threshold: 0.15 }
    );

    if (containerRef.current) {
      observer.observe(containerRef.current);
    }

    return () => observer.disconnect();
  }, [animationKey]);

  const replay = () => {
    setIsVisible(false);
    setTimeout(() => {
      setAnimationKey((k) => k + 1);
      setIsVisible(true);
    }, 50);
  };

  return (
    <figure className={`relative group ${className}`}>
      <div
        ref={containerRef}
        key={animationKey}
        onClick={replay}
        className={`relative overflow-hidden cursor-pointer ${aspectRatio}`}
      >
        {/* The Image underneath */}
        <img
          src={src}
          alt={alt}
          className={`${imageClassName} transition-all duration-1000 ease-out ${
            isVisible ? 'scale-100 opacity-100' : 'scale-110 opacity-40'
          }`}
        />

        {/* The Sliding Reveal Block (Covers image and slides off to reveal it) */}
        <div
          className={`absolute inset-0 w-full h-full z-10 pointer-events-none transition-transform duration-1000 ease-[cubic-bezier(0.77,0,0.175,1)] ${blockColor} ${
            isVisible ? 'translate-x-full' : 'translate-x-0'
          }`}
          style={{ transitionDelay: `${delay}ms` }}
        />

        {/* Subtle hover vignette */}
        <div className="absolute inset-0 bg-black/10 group-hover:bg-transparent transition-colors pointer-events-none" />
      </div>
    </figure>
  );
}
