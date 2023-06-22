import React from "react";
import { Heading, Flex, Divider, Image } from "@chakra-ui/react";

const Header = () => {
    return (
        <Flex
        as="nav"
        align="center"
        justify="space-between"
        wrap="wrap"
        padding="0.5rem"
        bg="gray.400"
        >
        <Flex align="center" mr={8}>
        <Heading as="h1" size="md"><span id="header-first">BTP2</span> Network Status Monitor</Heading>
        <Divider flex='1' />
        </Flex>
        </Flex>
    );
};

export default Header;
