import { ArrowForwardIcon, RepeatIcon } from "@chakra-ui/icons";
import { Badge, Box, Divider, Flex, IconButton, Spinner, Tag, Text, Tooltip } from "@chakra-ui/react";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import React, {Label} from "react";
import NetworkInfo from "./Network";

const COLOR_FOR = {
    good: 'green',
    bad: 'red'
}

const LinkDescItem = ({title, desc, value}) => {
    return (
        <Flex fontSize="sm">
            <Flex flex="1" justifyContent="right">
            <Tooltip label={desc || ""}>{title}</Tooltip>
            &nbsp;&bull;&nbsp;
            </Flex>
            <Flex flex="1">
             {value}
            </Flex>
        </Flex>
    )
}

const Link = ({url, link}) => {
    const queryClient = useQueryClient();
    const queryKey = ["link", link.src, link.dst];
    const statusQuery = useQuery(queryKey, async () => {
        const res = await fetch(url+"/links/"+link["src"]+"/"+link["dst"]);
        return await res.json();
    }, {
        staleTime: 10000,
        cacheTime: 5000,
        refetchInterval: 10000,
    });

    if (!statusQuery.isFetched) {
        return (<p>Loading</p>)
    }

    const status = statusQuery.data;
    const updateStatus = (event: Event) => {
        queryClient.invalidateQueries(queryKey);
    }

    return (
        <Box p="2" borderColor="gray.400" borderWidth="1px" borderRadius="lg" margin="2px" width="50%" id="link-info">
        <Flex>
            <Flex flex="1">
            <NetworkInfo url={url} id={status.src} name={status.src_name} />
            &nbsp;
            <ArrowForwardIcon margin="0.3" />
            &nbsp;
            <NetworkInfo url={url} id={status.dst} name={status.dst_name} />
            </Flex>
            {status.tx_seq > status.rx_seq && <Flex>Delivering<IconButton size="xs" margin="2px" isLoading="true" /></Flex>}
            <IconButton margin="2px" size="xs" onClick={updateStatus} isLoading={statusQuery.isLoading} icon={<RepeatIcon />} />
        </Flex>
        <Divider />
        <Flex id="link-description">
        <LinkDescItem title="TX Sequence" value={status.tx_seq} />
        <LinkDescItem title="RX Sequence" value={status.rx_seq} />
        <LinkDescItem title="TX Height" desc='Last block height of source blockchain' value={status.tx_height} />
        <LinkDescItem title="RX Height" desc='Last block height of BMV in target blockchain' value={status.rx_height} />
        <LinkDescItem title="Pending Count" desc='Pending message count' value={status.pending_count} />
        <LinkDescItem title="Pending Delay" desc='Delay after first pending message' value={status.pending_delay} />
        </Flex>
        <Divider />
        <Flex id="network-state">
        <Badge flex="1" textAlign="center" fontSize="lg" colorScheme={COLOR_FOR[status.state]}>{String(status.state).toUpperCase()}</Badge>
        </Flex>
        </Box>
    );
}

export default Link;