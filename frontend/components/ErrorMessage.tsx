import { ExclamationTriangleIcon, XMarkIcon } from '@heroicons/react/24/outline';
import { motion } from 'framer-motion';

interface ErrorMessageProps {
  message: string;
  title?: string;
  onDismiss?: () => void;
  variant?: 'error' | 'warning' | 'info';
}

const variantStyles = {
  error: {
    container: 'bg-red-50 border-red-200 text-red-800',
    icon: 'text-red-400',
    button: 'text-red-400 hover:text-red-600',
  },
  warning: {
    container: 'bg-yellow-50 border-yellow-200 text-yellow-800',
    icon: 'text-yellow-400',
    button: 'text-yellow-400 hover:text-yellow-600',
  },
  info: {
    container: 'bg-blue-50 border-blue-200 text-blue-800',
    icon: 'text-blue-400',
    button: 'text-blue-400 hover:text-blue-600',
  },
};

export default function ErrorMessage({ 
  message, 
  title, 
  onDismiss, 
  variant = 'error' 
}: ErrorMessageProps) {
  const styles = variantStyles[variant];

  return (
    <motion.div
      initial={{ opacity: 0, y: -10 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -10 }}
      className={`rounded-lg border p-4 ${styles.container}`}
    >
      <div className="flex">
        <div className="flex-shrink-0">
          <ExclamationTriangleIcon className={`h-5 w-5 ${styles.icon}`} />
        </div>
        <div className="ml-3 flex-1">
          {title && (
            <h3 className="text-sm font-medium mb-1">
              {title}
            </h3>
          )}
          <p className="text-sm">
            {message}
          </p>
        </div>
        {onDismiss && (
          <div className="ml-auto pl-3">
            <div className="-mx-1.5 -my-1.5">
              <button
                type="button"
                onClick={onDismiss}
                className={`inline-flex rounded-md p-1.5 focus:outline-none focus:ring-2 focus:ring-offset-2 ${styles.button}`}
              >
                <span className="sr-only">Dismiss</span>
                <XMarkIcon className="h-5 w-5" />
              </button>
            </div>
          </div>
        )}
      </div>
    </motion.div>
  );
}
