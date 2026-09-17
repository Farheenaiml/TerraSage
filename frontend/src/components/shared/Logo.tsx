import { Sprout } from 'lucide-react';
import { cn } from '@/lib/utils';

interface LogoProps {
  className?: string;
  size?: 'sm' | 'md' | 'lg';
  showText?: boolean;
}

const sizeMap = {
  sm: { icon: 'h-7 w-7', text: 'text-base', sub: 'text-[9px]' },
  md: { icon: 'h-9 w-9', text: 'text-lg', sub: 'text-[10px]' },
  lg: { icon: 'h-12 w-12', text: 'text-2xl', sub: 'text-xs' },
};

export function Logo({ className, size = 'md', showText = true }: LogoProps) {
  const s = sizeMap[size];
  return (
    <div className={cn('flex items-center gap-2.5', className)}>
      <div className={cn('flex items-center justify-center rounded-lg bg-primary', s.icon)}>
        <Sprout className={cn('text-primary-foreground', size === 'lg' ? 'h-7 w-7' : 'h-5 w-5')} />
      </div>
      {showText && (
        <div>
          <span className={cn('font-display font-semibold text-foreground', s.text)}>TerraSage</span>
          <span className={cn('block font-medium uppercase tracking-wider text-muted-foreground', s.sub)}>
            Environmental Intelligence
          </span>
        </div>
      )}
    </div>
  );
}
