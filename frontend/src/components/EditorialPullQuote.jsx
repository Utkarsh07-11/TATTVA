import React from 'react';

export default function EditorialPullQuote({ quote, author, role, location }) {
  return (
    <figure className="my-10 max-w-4xl mx-auto px-6">
      <blockquote className="story-pullquote py-2">
        <p className="font-editorial italic text-2xl sm:text-3xl text-[#f1f5f9] leading-snug tracking-tight">
          "{quote}"
        </p>
      </blockquote>
      <figcaption className="mt-4 pl-8 flex items-center gap-3">
        <div className="w-8 h-[1px] bg-story-accent" />
        <div className="text-xs font-mono tracking-wider uppercase text-slate-400">
          <span className="text-white font-semibold">{author}</span>
          {role && <span className="text-slate-500"> — {role}</span>}
          {location && <span className="text-story-accent"> · {location}</span>}
        </div>
      </figcaption>
    </figure>
  );
}
