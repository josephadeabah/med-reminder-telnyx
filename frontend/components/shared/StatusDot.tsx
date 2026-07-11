// frontend/src/components/shared/StatusDot.tsx
export function StatusDot({ className, pulsing }: { className: string; pulsing?: boolean }) {
  return (
    <span className="relative inline-flex h-2.5 w-2.5 shrink-0">
      {pulsing && (
        <span className={`absolute inline-flex h-full w-full animate-ping rounded-full ${className} opacity-40`} />
      )}
      <span className={`relative inline-flex h-2.5 w-2.5 rounded-full ${className}`} />
    </span>
  );
}