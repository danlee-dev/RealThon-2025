import React, { InputHTMLAttributes, forwardRef } from 'react';
import styles from './Input.module.css';

interface InputProps extends InputHTMLAttributes<HTMLInputElement> {
    label?: string;
    error?: string;
}

const Input = forwardRef<HTMLInputElement, InputProps>(
    ({ label, error, className = '', ...props }, ref) => {
        return (
            <div className="w-full">
                {label && (
                    <label className={styles.label} htmlFor={props.id}>
                        {label}
                    </label>
                )}
                <input
                    ref={ref}
                    className={`${styles.input} ${error ? styles.error : ''} ${className}`}
                    {...props}
                />
                {error && <p className={styles.errorText}>{error}</p>}
            </div>
        );
    }
);

Input.displayName = 'Input';

export default Input;
