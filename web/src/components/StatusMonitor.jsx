import { Box, Flex } from "@chakra-ui/react";
import { useQuery } from "@tanstack/react-query";
import React from "react";
import Link from "./Link";

const StatusMonitor = ({url, link}) => {
    const links = useQuery(["links"], async () => {
        const res = await fetch(url+"/links");
        const jso = await res.json();
        return jso;
    }, {
        staleTime: 10000
    }).data;
    return (
        <Box margin="2px">
        {links ? links.map((link) => (
            <Flex margin="2px" key={link.src+"-"+link.dst}>
            <Link url={url} link={link} key={link.src+"-"+link.dst} />
            <Link url={url} link={{src: link.dst, dst: link.src}} key={link.dst+"-"+link.src} />
            </Flex>
        )) : <div>Loading</div> }
        </Box>
    );
};

export default StatusMonitor;