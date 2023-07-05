import React from "react";
import { Heading, Flex, Badge } from "@chakra-ui/react";
import { useQuery } from "@tanstack/react-query";

const Header = () => {
    const versionQuery = useQuery(["version"], async () => {
        const res = await fetch('/version');
        return await res.json();
    }, {
        staleTime: Infinity,
        cacheTime: Infinity,
    })
    return (
        <Flex
        as="nav"
        align="center"
        justify="space-between"
        padding="0.5rem"
        bg="gray.400"
        >
        <Flex align="center" flex="1">
        <Heading as="h1" size="md" flex="1"><span id="header-first">BTP2</span> Network Status Monitor</Heading>
        <Badge size="xs">
        <a href="https://github.com/iconloop/btp2-network-monitor">
        {versionQuery.isFetched ? versionQuery.data : "..."}
        </a>
        </Badge>
        </Flex>
        </Flex>
    );
};

export default Header;
