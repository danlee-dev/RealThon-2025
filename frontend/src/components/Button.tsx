import React, { ButtonHTMLAttributes } from 'react';
import styles from './Button.module.css';

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
    variant?: 'primary' | 'secondary' | 'outline';
    size?: 'sm' | 'md' | 'lg';
    isLoading?: boolean;
    className?: string;
    children: React.ReactNode;
}

export default function Button({
    variant = 'primary',
    size = 'md',
    isLoading = false,
    children,
    className = '',
    disabled,
    ...props
}: ButtonProps) {
    return (
        <button
            className={`
                ${styles.btn} 
                ${styles[variant]} 
                ${styles[size]}
                ${className}
            `}
            disabled={disabled || isLoading}
            {...props}
        >
            {isLoading && <div className={styles.spinner} />}
            {children}
        </button>
    );
}
