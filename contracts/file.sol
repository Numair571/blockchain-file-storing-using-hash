// SPDX-License-Identifier: MIT
pragma solidity >=0.4.22 <0.9.0;

contract file {
  address[] _owners;
  string[] _files;

  mapping(string=>bool) _f;

  function uploadFile(address owner,string memory filehash) public {
      require(!_f[filehash]);
      _owners.push(owner);
      _files.push(filehash);
      _f[filehash]=true;
  }

  function viewFiles() public view returns(address[] memory,string[] memory) {
    return(_owners,_files);

  }
}
