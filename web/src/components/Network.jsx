import {
    HStack,
    Heading,
    IconButton,
    Popover, PopoverArrow, PopoverBody,
    PopoverCloseButton,
    PopoverContent,
    PopoverHeader, PopoverTrigger,
    Table, Tbody, Tr, Td, Th,
    Tooltip, Box,
} from "@chakra-ui/react";
import { useQuery } from "@tanstack/react-query";
import React, { useRef } from "react";
import { FeeTableIcon } from "./Icons";
import RelayFeeTable from "./FeeTable";

const NetworkInfo = ({url, id, name}) =>  {
    const infoQuery = useQuery( ["networkInfo", id], async () => {
            const res = await fetch(url+"/network/"+id)
            const jso = await res.json();
            return jso;
        },
        {
            staleTime: Infinity,
            cacheTime: Infinity,
        },
    );
    const makeInfoContent = (info: any) => {
        return (
            <Table size="sm">
                <Tbody>
                    <Tr><Th>Type</Th><Td>{info.type}</Td></Tr>
                    <Tr><Th>Network</Th><Td>{info.network}</Td></Tr>
                    { info.name && <Tr><Th>Name</Th><Td>{info.name}</Td></Tr> }
                    { info.endpoint && <Tr><Th>EndPoint</Th><Td>{info.endpoint}</Td></Tr> }
                    { info.tx_limit && <Tr><Th>TxLimit</Th><Td isNumeric>{info.tx_limit} seconds</Td></Tr> }
                    { info.rx_limit && <Tr><Th>RxLimit</Th><Td isNumeric>{info.rx_limit} seconds</Td></Tr> }
                    { info.bmc && <Tr><Th>BMC</Th><Td>{info.bmc}</Td></Tr> }
                    { info.bmcm && <Tr><Th>BMCM</Th><Td>{info.bmcm}</Td></Tr> }
                    { info.bmcs && <Tr><Th>BMCS</Th><Td>{info.bmcs}</Td></Tr> }
                </Tbody>
            </Table>
        )
    };
    const initialFocus = useRef();

    return (
        <HStack>
        <Popover isLazy="true" preventOverflow="true" boundary="scrollParent"
            initialFocusRef={initialFocus}>
            <Tooltip hasArrow label="Show basic information" placement="top">
            <Box>
            <PopoverTrigger>
            <Heading size="sm" className="network-name">{name}</Heading>
            </PopoverTrigger>
            </Box>
            </Tooltip>
            <PopoverContent width="auto" className='network-info' borderColor="gray.400" marginLeft="6px">
                <PopoverArrow bg="gray.300" />
                <PopoverCloseButton ref={initialFocus} />
                <PopoverHeader bg="gray.200">
                    <Heading size="sm">{name} - Basic</Heading>
                </PopoverHeader>
                <PopoverBody>
                    {infoQuery.isLoading ? <Heading>Loading</Heading> : makeInfoContent(infoQuery.data)}
                </PopoverBody>
            </PopoverContent>
        </Popover>
        <Popover isLazy="true" preventOverflow="true" boundary="scrollParent">
            <Tooltip hasArrow label="Show fee table" placement="top">
            <Box>
            <PopoverTrigger>
            <IconButton size="xs" icon={<FeeTableIcon />}/>
            </PopoverTrigger>
            </Box>
            </Tooltip>
            <PopoverContent width="auto" className='fee-table' borderColor="gray.400" marginLeft="6px">
            <PopoverArrow bg="gray.300" />
            <PopoverHeader bg="gray.200">
                <Heading size="sm">{name} - Fee Table</Heading>
            </PopoverHeader>
            <PopoverBody>
                <RelayFeeTable url={url} id={id}/>
            </PopoverBody>
            </PopoverContent>
        </Popover>
        </HStack>
    )
};

export default NetworkInfo;