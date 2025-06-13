import type { AppProps } from 'next/app';
import { SWRConfig } from 'swr';
import { Toaster } from 'react-hot-toast';
import { Inter } from 'next/font/google';
import Head from 'next/head';

import '../styles/globals.css';
import { fetcher } from '../lib/api';
import Layout from '../components/Layout';

const inter = Inter({ subsets: ['latin'] });

export default function App({ Component, pageProps }: AppProps) {
  return (
    <>
      <Head>
        <title>EV Charging Analytics Platform</title>
        <meta name="description" content="Electric Vehicle Charging Analytics Platform" />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <link rel="icon" href="/favicon.ico" />
      </Head>
      
      <div className={inter.className}>
        <SWRConfig
          value={{
            fetcher,
            refreshInterval: 60000, // Refresh every 60 seconds for data analysis
            revalidateOnFocus: true,
            revalidateOnReconnect: true,
            errorRetryCount: 3,
            errorRetryInterval: 5000,
          }}
        >
          <Layout>
            <Component {...pageProps} />
          </Layout>

          <Toaster
            position="top-right"
            toastOptions={{
              duration: 4000,
              style: {
                background: '#363636',
                color: '#fff',
              },
              success: {
                duration: 3000,
                iconTheme: {
                  primary: '#22c55e',
                  secondary: '#fff',
                },
              },
              error: {
                duration: 5000,
                iconTheme: {
                  primary: '#ef4444',
                  secondary: '#fff',
                },
              },
            }}
          />
        </SWRConfig>
      </div>
    </>
  );
}
