import React, { FC, ReactElement } from 'react';

interface MetaProps {
    description?: string;
    tag?: string;
    author?: string;
}

interface NavProps {
    url: string;
    name: string;
}

const HeadComponent: FC<{ title: string; meta: MetaProps }> = ({ title, meta }) => (
    <>
        {meta.description && (
            <meta name="description" content={meta.description} />
        )}
        {meta.tag && <meta name="keywords" content={meta.tag} />}
        {meta.author && <meta name="author" content={meta.author} />}
    </>
);

const config = {
    footer: <p>MIT 2023 © Nextra.</p>,
    head: HeadComponent,
    readMore: 'Read More →',
    postFooter: null as ReactElement | null,
    darkMode: false,
    navs: [
        {
            url: 'https://github.com/shuding/nextra',
            name: 'Nextra'
        }
    ] as NavProps[]
};

export default config;
